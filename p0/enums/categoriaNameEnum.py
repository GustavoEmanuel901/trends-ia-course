from enum import Enum

class Categoria_Name(str, Enum):
    OPERACIONAL = "operacional"
    SUPORTE_HARDWARE = "suporte_tecnico_hardware"
    SUPORTE_SOFTWARE = "suporte_tecnico_software"
    VENDAS = "vendas"
    OUTROS = "outros"