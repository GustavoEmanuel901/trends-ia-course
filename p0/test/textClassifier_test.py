from json import JSONDecodeError, JSONDecoder
from unittest.mock import MagicMock, patch

import httpx
import pytest
from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    ContentFilterFinishReasonError,
    LengthFinishReasonError,
    PermissionDeniedError
)

from pydantic import BaseModel, ValidationError

from usecases.textClassifier import classify_text
from enums.MessagesTextEnum import MessagesEnum
from errors.classificationError import ClassificationError
from models.classificacaoTexto import ClassificacaoTexto

@pytest.fixture
def env_ok(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test-123")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")


def _make_http_error(error_cls, status_code):
    request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
    response = httpx.Response(status_code=status_code, request=request)
    return error_cls(f"HTTP error with status code {status_code}", response=response, body=None)

def _make_pydantic_validation_error() -> ValidationError:
    class DummyModel(BaseModel):
        campo_obrigatorio: int

    try:
        DummyModel(campo_obrigatorio="invalido")
    except ValidationError as exc:
        return exc
    raise AssertionError("Era esperado uma ValidationError")

@pytest.mark.parametrize(
"var_name, expected_msg",
    [
        ("LLM_API_KEY", MessagesEnum.MISSING_API_KEY),
        ("LLM_BASE_URL", MessagesEnum.MISSING_BASE_URL),
        ("LLM_MODEL", MessagesEnum.MISSING_MODEL),
    ],
)
def test_variaveis_ambiente_ausentes_ou_vazias(env_ok, monkeypatch, var_name, expected_msg):
    monkeypatch.setenv(var_name, "")
    with pytest.raises(ClassificationError) as exc:
        classify_text("Olá, preciso de suporte")
    assert str(exc.value.args[0]) == expected_msg

@pytest.mark.parametrize(
    "url_invalida",
    [
        "ftp://api.openai.com/v1",            
        "https://",                            
        "https://user:pass@api.openai.com/v1",
        "https://api.openai.com/v1?a=1",       
        "https://api.openai.com/v1#sec",       
        "https://api.openai.com/v 1",         
        'https://api.openai.com/"v1"',         
        "http://[::1",                         
    ],
)
def test_base_url_invalida(env_ok, monkeypatch, url_invalida):
    monkeypatch.setenv("LLM_BASE_URL", url_invalida)
    with pytest.raises(ClassificationError) as exc:
        classify_text("Olá, preciso de suporte.")
    assert exc.value.args[0] == MessagesEnum.INVALID_BASE_URL


@patch("usecases.textClassifier.OpenAI")
def test_classify_text_sucesso(mock_openai, env_ok):
    resultado_esperado = MagicMock(spec=ClassificacaoTexto)

    mock_client = mock_openai.return_value.__enter__.return_value
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(parsed=resultado_esperado))]
    mock_client.beta.chat.completions.parse.return_value = mock_completion

    resultado = classify_text("Quero cancelar minha assinatura.")

    assert resultado is resultado_esperado
    mock_openai.assert_called_once_with(
        base_url="https://api.openai.com/v1",
        api_key="sk-test-123",
        timeout=30.0,
        _strict_response_validation=True,
    )
    mock_client.beta.chat.completions.parse.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Você é um sistema de triagem. Classifique o texto do usuário estritamente nas categorias definidas.",
            },
            {
                "role": "user",
                "content": "Quero cancelar minha assinatura.",
            },
        ],
        response_format=ClassificacaoTexto,
        temperature=0,
        max_tokens=1024,
    )

@pytest.mark.parametrize(
    "choices_mock",
    [
        [],                                       
        [MagicMock(message=MagicMock(parsed=None))],
    ],
)
@patch("usecases.textClassifier.OpenAI")
def test_resposta_sem_parsed_valido(mock_openai, env_ok, choices_mock):
    mock_client = mock_openai.return_value.__enter__.return_value
    mock_client.beta.chat.completions.parse.return_value = MagicMock(choices=choices_mock)

    with pytest.raises(ClassificationError) as exc:
        classify_text("Texto válido")
    assert exc.value.args[0] == MessagesEnum.BAD_FORMAT_RESPONSE

@pytest.mark.parametrize(
    "excecao_simulada, mensagem_esperada",
    [
        (APITimeoutError(request=MagicMock()), MessagesEnum.TIMEOUT_ERROR),
        (APIConnectionError(request=MagicMock()), MessagesEnum.CONNECTION_ERROR),
        (_make_http_error(AuthenticationError, 401), MessagesEnum.AUTHENTICATION_ERROR),
        (_make_http_error(PermissionDeniedError, 403), MessagesEnum.AUTHENTICATION_ERROR),
        (_make_http_error(APIStatusError, 404), MessagesEnum.NOT_FOUND_ERROR),
        (_make_http_error(APIStatusError, 429), MessagesEnum.RATE_LIMIT_ERROR),
        (_make_http_error(APIStatusError, 500), MessagesEnum.SERVICE_UNAVAILABLE_ERROR),
        (_make_http_error(APIStatusError, 503), MessagesEnum.SERVICE_UNAVAILABLE_ERROR),
        (_make_http_error(APIStatusError, 422), MessagesEnum.SERVICE_RESTRICTED_ERROR),
        (
            APIResponseValidationError(response=MagicMock(), body=None),
            MessagesEnum.INVALID_RESPONSE,
        ),
        (_make_pydantic_validation_error(), MessagesEnum.INVALID_RESPONSE),
        (JSONDecodeError("Erro JSON", "doc", 0), MessagesEnum.INVALID_RESPONSE),
        (LengthFinishReasonError(completion=MagicMock()), MessagesEnum.INVALID_RESPONSE),
        (ContentFilterFinishReasonError(), MessagesEnum.FILTERED_CONTENT_ERROR),
        (AttributeError("atributo inexistente"), MessagesEnum.BAD_FORMAT_RESPONSE),
        (TypeError("tipo inválido"), MessagesEnum.BAD_FORMAT_RESPONSE),
    ],
)
@patch("usecases.textClassifier.OpenAI")
def test_mapeamento_excecoes_openai(mock_openai, env_ok, excecao_simulada, mensagem_esperada):
    mock_client = mock_openai.return_value.__enter__.return_value
    mock_client.beta.chat.completions.parse.side_effect = excecao_simulada

    with pytest.raises(ClassificationError) as exc:
        classify_text("Texto válido")

    assert exc.value.args[0] == mensagem_esperada
    assert exc.value.__cause__ is excecao_simulada