from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.cambio_tools import consultar_cotacao
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState

system_prompt = (
    "Você é o Agente de Câmbio do Banco Ágil. "
    "Sua função é consultar cotações de moedas estrangeiras (USD, EUR, GBP, BTC) em relação ao Real (BRL). "
    "Use a ferramenta 'consultar_cotacao' informando a sigla da moeda."
    "Se o usuário pedir, use a ferramenta 'encerrar_atendimento'."
)

tools = [consultar_cotacao, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_cambio_node(state: BancoAgilState):
    response = agent.invoke({"messages": state["messages"]})
    new_messages = response["messages"][len(state["messages"]):]
    return {"messages": new_messages, "agente_atual": "cambio"}
