import os
import sys
import httpx
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

def main():
    
    entrada = input("Você: ").strip()
    
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
        resposta = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": entrada}],
            max_tokens=512,
        )
        print("\nAssistente:", resposta.choices[0].message.content)
    except Exception as e:
        print(f"Erro ao consultar o LLM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()