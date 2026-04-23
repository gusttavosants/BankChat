from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.cambio_tools import consultar_cotacao
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o consultor de Câmbio do Banco Ágil. Sua tarefa é fornecer cotações em tempo real para os clientes.\n\n"
    "Orientações de atendimento:\n"
    "- Ao falar sobre câmbio, apresente as moedas disponíveis: Dólar (USD), Euro (EUR), Libra (GBP) e Bitcoin (BTC).\n"
    "- Pergunte qual moeda o cliente deseja consultar e use a ferramenta 'consultar_cotacao' informando a sigla correspondente.\n"
    "- Se o cliente quiser tratar de outros assuntos (como crédito), anuncie a transição naturalmente antes de encerrar sua fala.\n\n"
    "Regras técnicas:\n"
    "- Mantenha a formatação de valores no padrão brasileiro (R$ X.XXX,XX).\n"
    "- Se o serviço de cotação estiver fora do ar, informe o problema de forma educada e sugira tentar novamente mais tarde, evitando expor logs ou códigos de erro."
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
        contexto_agente += "\nSua tarefa agora é: APRESENTE AS MOEDAS DISPONÍVEIS (USD, EUR, GBP, BTC) e pergunte qual o cliente deseja consultar."
        messages = messages + [
            SystemMessage(content=contexto_agente),
            HumanMessage(content="Olá! Por favor, me mostre as opções de câmbio.", name="system"),
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
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and "me mostre as opções de câmbio" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "cambio", "encerrado": encerrado}