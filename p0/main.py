from dotenv import load_dotenv
from usecases.textClassifier import classify_text
from usecases.getEntry import get_entry

load_dotenv()

def main():
    
    entrada = get_entry("Qual sua dúvida ou problema? ")
    if not entrada:
        return

    resultado = classify_text(entrada)

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