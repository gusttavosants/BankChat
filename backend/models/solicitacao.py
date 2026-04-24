from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class SolicitacaoAumento(BaseModel):
    cpf_cliente: str = Field(..., description="CPF do cliente solicitante")
    data_hora_solicitacao: datetime = Field(..., description="Data e hora da solicitação (ISO 8601)")
    limite_atual: float = Field(..., description="Limite antes da solicitação")
    novo_limite_solicitado: float = Field(..., description="Novo limite desejado")
    status_pedido: Literal["pendente", "aprovado", "rejeitado"] = Field(..., description="Status da solicitação")
