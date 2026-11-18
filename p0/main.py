import os
import sys
import httpx
from openai import OpenAI
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class Categoria_Name(str, Enum):
    OPERACIONAL = "operacional"
    SUPORTE_HARDWARE = "suporte_tecnico_hardware"
    SUPORTE_SOFTWARE = "suporte_tecnico_software"
    VENDAS = "vendas"
    OUTROS = "outros"

    class Categoria_ID(int, Enum):
        OPERACIONAL = 1
        SUPORTE_HARDWARE = 2
        SUPORTE_SOFTWARE = 3
        VENDAS = 4
        OUTROS = 5

class ClassificacaoTexto(BaseModel):
    categoria_id: Categoria_Name.Categoria_ID = Field(description="O ID da categoria principal do texto.")
    categoria_nome: Categoria_Name = Field(description="A categoria principal do texto.")
    resumo: str = Field(description="Resumo do problema em até 10 palavras.")

def main():
    
    entrada = input("Qual sua dúvida ou problema? ").strip()
    
    if not entrada:
        print("Entrada vazia. Encerrando.")
        return

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL") 

    http_client = httpx.Client()

    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=http_client
        )
        resposta = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                { 
                    "role": "system",
                    "content": "Você é um sistema de triagem. Classifique o texto do usuário estritamente nas categorias definidas."
                },
                {
                    "role": "user",
                    "content": entrada
                }
            ],
            response_format=ClassificacaoTexto,
            temperature=0,
            max_tokens=1024,
        )
        
        resultado = resposta.choices[0].message.parsed        

        print("\n--- Resultado da Classificação ---")
        print(f"Categoria ID: {resultado.categoria_id.value}")  
        print(f"Categoria:  {resultado.categoria_nome.value}")
        print(f"Resumo:     {resultado.resumo}")

    except Exception as e:
        print(f"Erro ao consultar o LLM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    while True:
        main()
        continuar = input("Deseja tirar mais dúvidas? (s/n): ").strip().lower()
        if continuar != "s":
            break