from models.llmParams import LLMParams

def get_input(prompt: str, default: float) -> float:
    value = input(prompt).strip()

    if not value:
        return default

    try:
        value = float(value)
    except ValueError:
        print(f"Valor inválido, usando padrão: {default}")
        return default

    return value


def get_llm_params() -> LLMParams:

    not_usar_defaults = input("Deseja alterar os valores padrão para os parâmetros do LLM? (s/n): ").strip().lower() == "s"

    if not not_usar_defaults:
        return LLMParams(timeout=30.0, temperature=0.0, max_tokens=1024)
  
    timeout = get_input("Qual o timeout para a requisição? (Padrão: 30.0) ", 30.0)

    temperature = get_input("Qual a temperatura para a geração do texto? (Padrão: 0.0) ", 0.0)
   
    max_tokens = int(get_input("Qual o número máximo de tokens para a geração do texto? (Padrão: 1024) ", 1024))

    return LLMParams(timeout=timeout, temperature=temperature, max_tokens=max_tokens)