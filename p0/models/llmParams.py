from pydantic import BaseModel, Field

class LLMParams(BaseModel):
    timeout: float = Field(description="O tempo limite para a requisição.")
    temperature: float = Field(description="A temperatura para a geração do texto.")
    max_tokens: int = Field(description="O número máximo de tokens para a geração do texto.")