from models.llmParams import LLMParams
from logger_config import get_logger


logger = get_logger("text_classifier.llm_params")


def get_input(prompt: str, default: float) -> float:
    value = input(prompt).strip()

    if not value:
        logger.debug(f"Entrada vazia, usando valor padrão: {default}")
        return default

    try:
        value = float(value)
        logger.debug(f"Valor convertido com sucesso: {value}")
    except ValueError:
        logger.warning(f"Valor inválido fornecido, usando padrão: {default}")
        print(f"Valor inválido, usando padrão: {default}")
        return default

    return value


def get_llm_params() -> LLMParams:
    logger.info("Iniciando configuração de parâmetros do LLM")
    
    not_usar_defaults = input("Deseja alterar os valores padrão para os parâmetros do LLM? (s/n): ").strip().lower() == "s"

    if not not_usar_defaults:
        logger.info("Usando valores padrão do LLM: timeout=30.0, temperature=0.0, max_tokens=1024")
        return LLMParams(timeout=30.0, temperature=0.0, max_tokens=1024)
  
    logger.info("Configurando parâmetros customizados do LLM")
    
    timeout = get_input("Qual o timeout para a requisição? (Padrão: 30.0) ", 30.0)
    temperature = get_input("Qual a temperatura para a geração do texto? (Padrão: 0.0) ", 0.0)
    max_tokens = int(get_input("Qual o número máximo de tokens para a geração do texto? (Padrão: 1024) ", 1024))

    logger.info(f"Parâmetros customizados configurados: timeout={timeout}, temperature={temperature}, max_tokens={max_tokens}")
    
    return LLMParams(timeout=timeout, temperature=temperature, max_tokens=max_tokens)