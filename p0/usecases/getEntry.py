from logger_config import get_logger


logger = get_logger("text_classifier.entry")


def get_entry(prompt: str) -> str | None:
    logger.debug("Aguardando entrada do usuário")
    entrada = input(f"{prompt}: ").strip()
    
    if not entrada:
        logger.info("Entrada vazia recebida do usuário")
        print("Entrada vazia. Encerrando.")
        return None
    
    logger.debug(f"Entrada recebida do usuário ({len(entrada)} caracteres)")
    return entrada