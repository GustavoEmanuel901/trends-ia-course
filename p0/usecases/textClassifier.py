import os
from json import JSONDecodeError
from urllib.parse import urlsplit

from enums.MessagesTextEnum import MessagesEnum
from openai import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    ContentFilterFinishReasonError,
    LengthFinishReasonError,
    OpenAI,
    PermissionDeniedError,
)
from pydantic import ValidationError

from models.classificacaoTexto import ClassificacaoTexto
from errors.classificationError import ClassificationError
from usecases.getLLMparams import get_llm_params
from models.llmParams import LLMParams
from logger_config import get_logger, mask_url


logger = get_logger("text_classifier.classifier")


def classify_text(text: str, llm_params: LLMParams) -> ClassificacaoTexto:
    logger.debug(f"Iniciando classificação de texto (tamanho: {len(text)} caracteres)")
    
    if not text.strip():
        logger.warning("Tentativa de classificar texto vazio")
        raise ClassificationError(MessagesEnum.EMPTY_TEXT)

    api_key = (os.getenv("LLM_API_KEY") or "").strip()
    base_url = (os.getenv("LLM_BASE_URL") or "").strip()
    model_name = (os.getenv("LLM_MODEL") or "").strip()
    
    if not api_key:
        logger.error("Variável de ambiente LLM_API_KEY não configurada")
        raise ClassificationError(MessagesEnum.MISSING_API_KEY)
    if not base_url:
        logger.error("Variável de ambiente LLM_BASE_URL não configurada")
        raise ClassificationError(MessagesEnum.MISSING_BASE_URL)
    if not model_name:
        logger.error("Variável de ambiente LLM_MODEL não configurada")
        raise ClassificationError(MessagesEnum.MISSING_MODEL)

    logger.debug(f"Configuração carregada: host={mask_url(base_url)}, model={model_name}")

    try:
        url = urlsplit(base_url)
        valid_url = (
            url.scheme in ("http", "https")
            and bool(url.hostname)
            and url.username is None
            and url.password is None
            and not url.query
            and not url.fragment
            and not any(c.isspace() or c in "\"'<>" for c in base_url)
        )
        _ = url.port
    except ValueError:
        valid_url = False
    
    if not valid_url:
        logger.error(f"URL de base inválida: {mask_url(base_url)}")
        raise ClassificationError(MessagesEnum.INVALID_BASE_URL)

    logger.info(f"Conectando ao servidor LLM: {mask_url(base_url)}")
    
    try:
        with OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=llm_params.timeout,
            _strict_response_validation=True,
        ) as client:
            logger.debug(f"Cliente OpenAI criado com timeout={llm_params.timeout}s")
            
            resposta = client.beta.chat.completions.parse(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um sistema de triagem. Classifique o texto do usuário estritamente nas categorias definidas.",
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                response_format=ClassificacaoTexto,
                temperature=llm_params.temperature,
                max_tokens=llm_params.max_tokens,
            )
            logger.debug("Resposta recebida do servidor LLM")
            
    except APITimeoutError as exc:
        logger.error(f"Timeout ao chamar API LLM (timeout={llm_params.timeout}s)", exc_info=True)
        raise ClassificationError(MessagesEnum.TIMEOUT_ERROR) from exc
    except APIConnectionError as exc:
        logger.error("Erro de conexão ao servidor LLM", exc_info=True)
        raise ClassificationError(MessagesEnum.CONNECTION_ERROR) from exc
    except (AuthenticationError, PermissionDeniedError) as exc:
        logger.error("Erro de autenticação com servidor LLM", exc_info=True)
        raise ClassificationError(MessagesEnum.AUTHENTICATION_ERROR) from exc
    except APIStatusError as exc:
        if exc.status_code == 404:
            message = MessagesEnum.NOT_FOUND_ERROR
            logger.error("Modelo ou endpoint não encontrado (404)", exc_info=True)
        elif exc.status_code == 429:
            message = MessagesEnum.RATE_LIMIT_ERROR
            logger.error("Limite de requisições atingido (429)", exc_info=True)
        elif exc.status_code >= 500:
            message = MessagesEnum.SERVICE_UNAVAILABLE_ERROR
            logger.error(f"Servidor LLM indisponível ({exc.status_code})", exc_info=True)
        else:
            message = MessagesEnum.SERVICE_RESTRICTED_ERROR
            logger.error(f"Erro HTTP do servidor ({exc.status_code})", exc_info=True)
        raise ClassificationError(message) from exc
    except (APIResponseValidationError, ValidationError, JSONDecodeError, LengthFinishReasonError) as exc:
        logger.error("Resposta inválida ou mal formatada do servidor LLM", exc_info=True)
        raise ClassificationError(MessagesEnum.INVALID_RESPONSE) from exc
    except ContentFilterFinishReasonError as exc:
        logger.warning("Conteúdo filtrado pelo servidor LLM", exc_info=True)
        raise ClassificationError(MessagesEnum.FILTERED_CONTENT_ERROR) from exc
    except (AttributeError, TypeError) as exc:
        logger.error("Erro ao processar resposta do servidor LLM", exc_info=True)
        raise ClassificationError(MessagesEnum.BAD_FORMAT_RESPONSE) from exc

    if not resposta.choices or resposta.choices[0].message.parsed is None:
        logger.error("Resposta do servidor sem dados parseados")
        raise ClassificationError(MessagesEnum.BAD_FORMAT_RESPONSE)

    resultado = resposta.choices[0].message.parsed
    logger.info("Classificação completada com sucesso")
    
    return resultado