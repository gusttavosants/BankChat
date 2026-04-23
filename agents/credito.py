from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente especializado em Crédito do Banco Ágil.\n\n"
    "SERVIÇOS:\n"
    "1. Consultar limite atual.\n"
    "2. Solicitar aumento de limite.\n\n"
    "DIRETRIZES:\n"
    "- Se o aumento for negado, ofereça realizar uma análise financeira detalhada agora mesmo.\n"
    "- Caso aceite a análise, confirme e finalize sua fala para que o setor de análise assuma.\n"
    "- Após consultas bem-sucedidas, ofereça: 1. Consultar Câmbio ou 2. Finalizar Atendimento.\n"
    "- Formate valores como R$ X.XXX,XX."
)

tools = [consultar_limite, solicitar_aumento, verificar_score_limite, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_credito_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "credito"
    
    contexto = "Setor: CRÉDITO.\n"
    if state.get("cliente_autenticado"):
        nome = state.get("dados_cliente", {}).get("nome", "Cliente")
        score = state.get("dados_cliente", {}).get("score_credito", "desconhecido")
        limite = state.get("dados_cliente", {}).get("limite_credito", "desconhecido")
        contexto += f"Cliente: {nome} | Score: {score} | Limite: {limite}\n"
        
        if state.get("analise_realizada"):
            contexto += "Nota: Análise financeira já realizada nesta sessão.\n"

    if transferencia:
        contexto += "Apresente o menu de Crédito e cumprimente o cliente."
        messages = messages + [
            SystemMessage(content=contexto),
            HumanMessage(content="Quais as opções de crédito?", name="system")
        ]
    else:
        messages = messages + [SystemMessage(content=contexto)]
    
    response = agent.invoke({"messages": messages})
    new_messages = response["messages"][len(messages):]
    
    encerrado = any(
        isinstance(m, ToolMessage) and '"encerrado": true' in m.content.lower()
        for m in new_messages
    )
    
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "credito"
            
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and "opções de crédito" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "credito", "encerrado": encerrado}
