from langgraph.prebuilt import create_react_agent
from core.config import LLM
from agents.cambio.tools import consultar_cotacao
from agents.shared.encerramento import encerrar_atendimento
from core.state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from utils.formatters import clean_llm_response

system_prompt = (
    "Você é o consultor de Câmbio do Banco Ágil. Sua tarefa é fornecer cotações em tempo real para os clientes.\n\n"
    "Orientações de atendimento:\n"
    "- Ao falar sobre câmbio, OBRIGATORIAMENTE apresente as moedas disponíveis de forma numerada: 1. Dólar (USD), 2. Euro (EUR), 3. Libra (GBP) e 4. Bitcoin (BTC).\n"
    "- Pergunte qual moeda o cliente deseja consultar e use a ferramenta 'consultar_cotacao' informando a sigla correspondente.\n"
    "- Se o cliente nao quiser mais consultar câmbio (responder 'nao', 'nada', 'pode encerrar', etc.), NUNCA encerre o atendimento diretamente. Em vez disso, pergunte: 'Deseja acessar o servico de Credito (1) ou prefere encerrar o atendimento (2)?'. Somente chame 'encerrar_atendimento' se o cliente escolher encerrar explicitamente.\n"
    "- Se o cliente quiser tratar de crédito, anuncie a transição naturalmente antes de encerrar sua fala.\n\n"
    "Regras técnicas:\n"
    "- Mantenha a formatação de valores no padrão brasileiro (ex: R$ 5,03 para Dólar). Atenção: a API retorna o valor com ponto decimal (ex: 5.03 significa cinco reais e três centavos). Não trate o ponto como separador de milhar.\n"
    "- Se o serviço de cotação estiver fora do ar, informe o problema de forma educada e sugira tentar novamente mais tarde, evitando expor logs ou códigos de erro.\n"
    "- NUNCA use emojis, asteriscos, underscores ou qualquer marcação markdown nas suas respostas. Use somente texto puro."
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
        contexto_agente += "\nSua tarefa agora é: APRESENTE AS MOEDAS DISPONÍVEIS (USD, EUR, GBP, BTC) e pergunte qual o cliente deseja consultar. IMPORTANTE: Não se apresente novamente nem dê boas-vindas, apenas forneça as opções de forma direta e natural."
        messages = messages + [
            SystemMessage(content=contexto_agente),
            HumanMessage(content="Gostaria de ver as opções de câmbio.", name="system"),
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
            isinstance(m, HumanMessage) and "opções de câmbio" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "cambio", "encerrado": encerrado}