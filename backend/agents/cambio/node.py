from langgraph.prebuilt import create_react_agent
from core.config import LLM
from agents.cambio.tools import consultar_cotacao
from agents.shared.encerramento import encerrar_atendimento
from core.state import BancoAgilState
from core.prompts import apply_global_rules
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from utils.formatters import clean_llm_response

system_prompt = apply_global_rules(
    "Você é o consultor de Câmbio do Banco Ágil. Sua única função é fornecer cotações de moedas.\n\n"
    "REGRAS DE OURO DO CÂMBIO:\n"
    "- NÃO ofereça 'Transferência Internacional' ou qualquer outro serviço. O Banco Ágil oferece APENAS cotações neste momento.\n"
    "- Quando o cliente chegar, apresente APENAS a lista de moedas: 1. Dólar (USD), 2. Euro (EUR), 3. Libra (GBP), 4. Bitcoin (BTC).\n"
    "- Se o cliente desejar outra coisa, informe que no momento só realizamos cotações.\n"
    "- Mantenha a resposta concisa. Não repita a lista de opções se já a forneceu no mesmo parágrafo.\n"
    "- Use a ferramenta 'consultar_cotacao' para obter os valores reais."
)

tools = [consultar_cotacao, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_cambio_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "cambio"
    
    # Consolidamos contexto dinâmico
    contexto_agente = "Você é o assistente de CÂMBIO do Banco Ágil.\n"
    if state.get("cliente_autenticado"):
        nome = state.get("dados_cliente", {}).get("nome", "Cliente")
        contexto_agente += f"- Atendendo agora: {nome}.\n"

    if transferencia:
        contexto_agente += "\nSua tarefa: Apresente as moedas para cotação. Seja direto."
        messages = messages + [
            SystemMessage(content=contexto_agente),
            HumanMessage(content="Quero ver o câmbio."),
        ]
    else:
        messages = messages + [SystemMessage(content=contexto_agente)]

    response = agent.invoke({"messages": messages})
    new_messages = response["messages"][len(messages):]
    
    # Verifica se a ferramenta de encerramento foi chamada
    encerrado = any(
        isinstance(m, ToolMessage) and '"encerrado": true' in m.content.lower()
        for m in new_messages
    )
    
    # Adiciona o nome do agente às mensagens para fins de UI
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "cambio"
            msg.content = clean_llm_response(msg.content)
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "Quero ver o câmbio."
        )]
            
    return {"messages": new_messages, "agente_atual": "cambio", "encerrado": encerrado}