from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.auth_tools import autenticar_cliente
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState

system_prompt = (
    "Você é o Agente de Triagem do Banco Ágil. "
    "Sua responsabilidade é saudar o cliente, solicitar seu CPF e data de nascimento, "
    "e usar a ferramenta 'autenticar_cliente' para autenticá-lo. "
    "Se o cliente falhar 3 vezes na autenticação, encerre o atendimento. "
    "Após a autenticação, identifique a intenção do cliente (crédito ou câmbio) e avise-o que você o transferirá. "
    "Caso o cliente deseje encerrar, use a ferramenta 'encerrar_atendimento'."
)

tools = [autenticar_cliente, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_triagem_node(state: BancoAgilState):
    response = agent.invoke({"messages": state["messages"]})
    # Retorna apenas as mensagens novas adicionadas pelo agente
    new_messages = response["messages"][len(state["messages"]):]
    return {"messages": new_messages, "agente_atual": "triagem"}
