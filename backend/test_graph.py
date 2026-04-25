import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.getcwd())

from core.graph import workflow
from langchain_core.messages import HumanMessage

def test_graph():
    memory = None # No memory for simple test
    app_graph = workflow.compile()
    
    input_state = {
        "messages": [HumanMessage(content="Olá")],
        "agente_atual": "triagem",
        "cliente_autenticado": False,
        "cpf_cliente": None,
        "dados_cliente": None,
        "tentativas_auth": 0,
        "encerrado": False,
        "ultimo_erro": None,
        "solicitacao_em_aberto": None,
        "analise_realizada": False,
    }
    
    config = {"configurable": {"thread_id": "test"}}
    
    try:
        print("Invoking graph...")
        result = app_graph.invoke(input_state, config)
        print("Result:", result.get("agente_atual"))
        print("Messages:", len(result.get("messages", [])))
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    load_dotenv(override=True)
    test_graph()
