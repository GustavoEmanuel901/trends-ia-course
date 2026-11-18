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


def classify_text(text: str) -> ClassificacaoTexto:
    if not text.strip():
        raise ClassificationError(MessagesEnum.EMPTY_TEXT)

    api_key = (os.getenv("LLM_API_KEY") or "").strip()
    base_url = (os.getenv("LLM_BASE_URL") or "").strip()
    model_name = (os.getenv("LLM_MODEL") or "").strip()
    if not api_key:
        raise ClassificationError(MessagesEnum.MISSING_API_KEY)
    if not base_url:
        raise ClassificationError(MessagesEnum.MISSING_BASE_URL)
    if not model_name:
        raise ClassificationError(MessagesEnum.MISSING_MODEL)

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
        raise ClassificationError(MessagesEnum.INVALID_BASE_URL)

    try:
        with OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0,
            _strict_response_validation=True,
        ) as client:
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
                temperature=0,
                max_tokens=1024,
            )
    except APITimeoutError as exc:
        raise ClassificationError(MessagesEnum.TIMEOUT_ERROR) from exc
    except APIConnectionError as exc:
        raise ClassificationError(MessagesEnum.CONNECTION_ERROR) from exc
    except (AuthenticationError, PermissionDeniedError) as exc:
        raise ClassificationError(MessagesEnum.AUTHENTICATION_ERROR) from exc
    except APIStatusError as exc:
        if exc.status_code == 404:
            message = MessagesEnum.NOT_FOUND_ERROR
        elif exc.status_code == 429:
            message = MessagesEnum.RATE_LIMIT_ERROR
        elif exc.status_code >= 500:
            message = MessagesEnum.SERVICE_UNAVAILABLE_ERROR
        else:
            message = MessagesEnum.SERVICE_RESTRICTED_ERROR
        raise ClassificationError(message) from exc
    except (APIResponseValidationError, ValidationError, JSONDecodeError, LengthFinishReasonError) as exc:
        raise ClassificationError(MessagesEnum.INVALID_RESPONSE) from exc
    except ContentFilterFinishReasonError as exc:
        raise ClassificationError(MessagesEnum.FILTERED_CONTENT_ERROR) from exc
    except (AttributeError, TypeError) as exc:
        raise ClassificationError(MessagesEnum.BAD_FORMAT_RESPONSE) from exc

    if not resposta.choices or resposta.choices[0].message.parsed is None:
        raise ClassificationError(MessagesEnum.BAD_FORMAT_RESPONSE)

    return resposta.choices[0].message.parsed