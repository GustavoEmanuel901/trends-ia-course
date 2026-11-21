import logging
import sys
from urllib.parse import urlsplit


def setup_logger(name: str = "text_classifier") -> logging.Logger:

    logger = logging.getLogger(name)
    
    if len(logger.handlers) > 0:
        return logger
    
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def mask_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
        return parsed.hostname or "[URL inválida]"
    except Exception:
        return "[URL não identificada]"


def get_logger(name: str = "text_classifier") -> logging.Logger:
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        setup_logger(name)
    return logger
