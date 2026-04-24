from pydantic import BaseModel, Field

class Cliente(BaseModel):
    cpf: str = Field(..., description="CPF do cliente no formato XXX.XXX.XXX-XX")
    nome: str = Field(..., description="Nome completo do cliente")
    data_nascimento: str = Field(..., description="Data de nascimento no formato DD/MM/YYYY")
    limite_credito: float = Field(..., description="Limite de crédito atual em BRL")
    score_credito: int = Field(..., ge=0, le=1000, description="Score de crédito de 0 a 1000")
