from dotenv import load_dotenv
from usecases.getLLMparams import get_llm_params
from usecases.textClassifier import ClassificationError, classify_text
from usecases.getEntry import get_entry

load_dotenv()

def main():
    llm_params = get_llm_params()

    entrada = get_entry("Qual sua dúvida ou problema? ")
    if not entrada:
        return

    try:
        resultado = classify_text(entrada, llm_params)
    except ClassificationError as exc:
        print(f"Não foi possível classificar: {exc}")
        return

    print("\n--- Resultado da Classificação ---")
    print(f"Categoria ID: {resultado.categoria_id.value}")  
    print(f"Categoria:  {resultado.categoria_nome.value}")
    print(f"Resumo:     {resultado.resumo}")


if __name__ == "__main__":
    while True:
        main()
        continuar = input("Deseja tirar mais dúvidas? (s/n): ").strip().lower()
        if continuar != "s":
            break