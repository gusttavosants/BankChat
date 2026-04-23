from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.cambio_tools import consultar_cotacao
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente virtual do Banco Ágil. "
    "Ao tratar de câmbio, apresente as opções seguindo este formato:\n\n"
    "Certo! Posso te ajudar com a cotação em tempo real de:\n\n"
    "1. Dólar (USD);\n"
    "2. Euro (EUR);\n"
    "3. Libra (GBP);\n"
    "4. Bitcoin (BTC).\n\n"
    "Qual moeda você gostaria de consultar?\n\n"
    "Use a ferramenta 'consultar_cotacao' informando a sigla da moeda desejada. "
    "IMPORTANTE: Se o cliente desejar tratar de outros assuntos (como crédito ou limite), diga naturalmente: 'Sem problemas! Vou verificar os detalhes de [Crédito/Triagem] para você...'. Isso acionará a transição interna.\n"
    "5. Se o cliente solicitar Crédito ou Triagem, anuncie a transição naturalmente.\n"
    "6. Formate valores monetários sempre no padrão brasileiro: R$ X.XXX,XX.\n\n"
    "TRATAMENTO DE ERROS TÉCNICOS:\n"
    "1. Se a ferramenta 'consultar_cotacao' retornar status 503 ou 500, informe: 'Desculpe, o serviço de cotação em tempo real está temporariamente indisponível. Posso tentar novamente em instantes ou você pode verificar outro serviço.'\n"
    "2. Se a moeda solicitada não for suportada (400), informe as moedas disponíveis cordialmente.\n"
    "3. NUNCA mostre erros de programação ao cliente."
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