import os
from openai import OpenAI
from models.classificacaoTexto import ClassificacaoTexto


def classify_text(text: str) -> ClassificacaoTexto:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL") 
    
    try:
        client = OpenAI(
        base_url=base_url,
            api_key=api_key, 
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
                        "content": text
                    }
                ],
                response_format=ClassificacaoTexto,
                temperature=0,
                max_tokens=1024,
            )

        return resposta.choices[0].message.parsed
    except Exception as e:
        print(f"Erro ao consultar o LLM: {e}")
        return None