from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.score_tools import calcular_score, atualizar_score
from state import BancoAgilState

system_prompt = (
    "Você é o Agente de Entrevista de Crédito do Banco Ágil. "
    "Você coleta conversacionalmente as seguintes informações financeiras do cliente: "
    "1. Renda mensal "
    "2. Tipo de emprego (formal, autônomo, desempregado) "
    "3. Despesas fixas mensais "
    "4. Número de dependentes (0, 1, 2, 3+) "
    "5. Se possui dívidas (sim/não) "
    "Após coletar todas as informações, use a ferramenta 'calcular_score'. "
    "Em seguida, use a ferramenta 'atualizar_score' passando o CPF do cliente. "
    "Informe o resultado ao cliente e avise que o retornará ao Agente de Crédito."
)

tools = [calcular_score, atualizar_score]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_entrevista_node(state: BancoAgilState):
    response = agent.invoke({"messages": state["messages"]})
    new_messages = response["messages"][len(state["messages"]):]
    return {"messages": new_messages, "agente_atual": "entrevista"}
