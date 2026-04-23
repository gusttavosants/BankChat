from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState

system_prompt = (
    "Você é o Agente de Crédito do Banco Ágil. "
    "Você auxilia clientes autenticados a consultar seu limite atual e solicitar aumento de limite. "
    "Use as ferramentas 'consultar_limite', 'solicitar_aumento', e 'verificar_score_limite'. "
    "Se a solicitação for rejeitada pelo score, você DEVE oferecer a Entrevista de Crédito para recalcular o score. "
    "Caso o cliente deseje encerrar, use a ferramenta 'encerrar_atendimento'."
)

tools = [consultar_limite, solicitar_aumento, verificar_score_limite, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_credito_node(state: BancoAgilState):
    response = agent.invoke({"messages": state["messages"]})
    new_messages = response["messages"][len(state["messages"]):]
    return {"messages": new_messages, "agente_atual": "credito"}
