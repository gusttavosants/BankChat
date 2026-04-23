from langchain.tools import tool

@tool
def encerrar_atendimento() -> dict:
    """Sinaliza que o atendimento deve ser encerrado. O agente atual deve se despedir do cliente após chamar esta ferramenta."""
    return {
        "status_code": 200,
        "message": "Atendimento encerrado.",
        "data": { "encerrado": True }
    }
