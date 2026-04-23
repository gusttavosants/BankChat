from typing import TypedDict, Optional, Annotated
import operator

def append_messages(existing: list, new: list) -> list:
    if not existing:
        existing = []
    if not isinstance(new, list):
        new = [new]
    return existing + new

class BancoAgilState(TypedDict):
    messages: Annotated[list, append_messages]
    cliente_autenticado: bool
    cpf_cliente: Optional[str]
    dados_cliente: Optional[dict]
    agente_atual: str
    tentativas_auth: int
    encerrado: bool
    ultimo_erro: Optional[str]
    solicitacao_em_aberto: Optional[dict]
