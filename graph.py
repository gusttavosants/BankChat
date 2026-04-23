from langgraph.graph import StateGraph, END
from state import BancoAgilState
from agents.triagem import agente_triagem_node
from agents.credito import agente_credito_node
from agents.entrevista import agente_entrevista_node
from agents.cambio import agente_cambio_node

def router(state: BancoAgilState):
    messages = state.get("messages", [])
    if not messages:
        return "triagem"
        
    last_message = messages[-1].content.lower()
    
    # Se a ferramenta encerrar_atendimento foi chamada (isso seria via tool message, 
    # mas simplificando podemos olhar o flag no state se houvesse, ou pela mensagem)
    if "encerrar" in last_message or "encerrado" in last_message:
        return END

    agente_atual = state.get("agente_atual", "triagem")
    
    if agente_atual == "triagem":
        if "crédito" in last_message or "credito" in last_message or "limite" in last_message:
            return "credito"
        elif "câmbio" in last_message or "cambio" in last_message or "moeda" in last_message or "cotação" in last_message:
            return "cambio"
        return END # Fica em triagem se não tomou decisão, mas LangGraph precisa retornar o mesmo nó ou esperar input

    if agente_atual == "credito":
        if "entrevista" in last_message or "recalcular" in last_message:
            return "entrevista"
        return END

    if agente_atual == "entrevista":
        if "crédito" in last_message or "credito" in last_message or "retornando" in last_message:
            return "credito"
        return END

    return END

# Constrói o grafo
workflow = StateGraph(BancoAgilState)

# Adiciona nós
workflow.add_node("triagem", agente_triagem_node)
workflow.add_node("credito", agente_credito_node)
workflow.add_node("entrevista", agente_entrevista_node)
workflow.add_node("cambio", agente_cambio_node)

# Define arestas e roteamento
workflow.set_entry_point("triagem")

workflow.add_conditional_edges(
    "triagem",
    router,
    {
        "credito": "credito",
        "cambio": "cambio",
        "entrevista": "entrevista",
        END: END
    }
)

workflow.add_conditional_edges(
    "credito",
    router,
    {
        "entrevista": "entrevista",
        END: END
    }
)

workflow.add_conditional_edges(
    "entrevista",
    router,
    {
        "credito": "credito",
        END: END
    }
)

workflow.add_conditional_edges(
    "cambio",
    router,
    {
        END: END
    }
)

app_graph = workflow.compile()
