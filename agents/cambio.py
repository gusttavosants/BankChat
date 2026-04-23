from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.cambio_tools import consultar_cotacao
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente de Câmbio do Banco Ágil.\n\n"
    "MOEDAS:\n"
    "- Dólar (USD), Euro (EUR), Libra (GBP), Bitcoin (BTC).\n\n"
    "DIRETRIZES:\n"
    "- Use 'consultar_cotacao' para obter valores reais.\n"
    "- Se o cliente quiser Crédito ou Triagem, anuncie a transição naturalmente.\n"
    "- Formate valores como R$ X.XXX,XX.\n"
    "- Em caso de falha técnica na API, peça desculpas e ofereça tentar mais tarde."
)

tools = [consultar_cotacao, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_cambio_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "cambio"
    
    contexto = "Setor: CÂMBIO.\n"
    if state.get("cliente_autenticado"):
        nome = state.get("dados_cliente", {}).get("nome", "Cliente")
        contexto += f"Atendendo: {nome}\n"

    if transferencia:
        contexto += "Apresente as moedas disponíveis e pergunte qual o cliente deseja."
        messages = messages + [
            SystemMessage(content=contexto),
            HumanMessage(content="Quais as opções de câmbio?", name="system"),
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
            msg.name = "cambio"
            
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and "opções de câmbio" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "cambio", "encerrado": encerrado}