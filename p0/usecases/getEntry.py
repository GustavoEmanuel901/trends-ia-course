def get_entry(prompt: str) -> str:
    entrada = input(prompt).strip()
    if not entrada:
        print("Entrada vazia. Encerrando.")
        return None
    return entrada