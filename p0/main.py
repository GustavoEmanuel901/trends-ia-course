from dotenv import load_dotenv
from usecases.getLLMparams import get_llm_params
from usecases.textClassifier import ClassificationError, classify_text
from usecases.getEntry import get_entry
from logger_config import get_logger

load_dotenv()

logger = get_logger("text_classifier.main")


def main():
    logger.info("Iniciando nova classificação")
    
    llm_params = get_llm_params()
    logger.debug(f"Parâmetros do LLM carregados: timeout={llm_params.timeout}s, temperature={llm_params.temperature}, max_tokens={llm_params.max_tokens}")

    entrada = get_entry("Qual sua dúvida ou problema? ")
    if not entrada:
        logger.info("Entrada vazia. Classificação cancelada.")
        return

    logger.info(f"Processando entrada (tamanho: {len(entrada)} caracteres)")
    
    try:
        resultado = classify_text(entrada, llm_params)
        logger.info(f"Classificação bem-sucedida. Categoria ID: {resultado.categoria_id.value}")
    except ClassificationError as exc:
        logger.error(f"Erro na classificação: {exc}")
        print(f"Não foi possível classificar: {exc}")
        return

    print("\n--- Resultado da Classificação ---")
    print(f"Categoria ID: {resultado.categoria_id.value}")  
    print(f"Categoria:  {resultado.categoria_nome.value}")
    print(f"Resumo:     {resultado.resumo}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Iniciando aplicação de classificação de texto")
    logger.info("=" * 60)
    
    try:
        while True:
            main()
            continuar = input("Deseja tirar mais dúvidas? (s/n): ").strip().lower()
            if continuar != "s":
                logger.info("Aplicação encerrada pelo usuário")
                break
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida por sinal de teclado")
    except Exception as exc:
        logger.error(f"Erro não tratado: {exc}", exc_info=True)
        raise