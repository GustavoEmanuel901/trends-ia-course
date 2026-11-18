from enum import Enum

class Categoria_ID(int, Enum):
        OPERACIONAL = 1
        SUPORTE_HARDWARE = 2
        SUPORTE_SOFTWARE = 3
        VENDAS = 4
        OUTROS = 5