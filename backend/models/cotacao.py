from pydantic import BaseModel, Field

class Cotacao(BaseModel):
    moeda: str = Field(..., description="Código da moeda de origem (ex: USD)")
    moeda_destino: str = Field(default="BRL", description="Código da moeda de destino")
    valor_compra: float = Field(..., description="Valor de compra na moeda destino")
    valor_venda: float = Field(..., description="Valor de venda na moeda destino")
    timestamp: str = Field(..., description="Timestamp ou data de atualização da cotação")
