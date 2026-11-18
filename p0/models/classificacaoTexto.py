from pydantic import BaseModel, Field
from enums.categoriaIDEnum import Categoria_ID
from enums.categoriaNameEnum import Categoria_Name

class ClassificacaoTexto(BaseModel):
    categoria_id: Categoria_ID = Field(description="O ID da categoria principal do texto.")
    categoria_nome: Categoria_Name = Field(description="A categoria principal do texto.")
    resumo: str = Field(description="Resumo do problema em até 10 palavras.")
