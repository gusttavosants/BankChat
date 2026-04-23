from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o especialista em Crédito do Banco Ágil. Seu objetivo é ajudar o cliente a consultar seu limite atual ou solicitar um aumento.\n\n"
    "Procedimentos de atendimento:\n"
    "- Ao iniciar, apresente o menu: 1. Consultar limite atual, 2. Solicitar aumento de limite.\n"
    "- Para consultas de limite, informe o valor e pergunte se ele deseja consultar o Câmbio ou encerrar o contato.\n"
    "- Se o cliente solicitar um aumento, peça o valor desejado e use 'solicitar_aumento'.\n"
    "- Caso o sistema negue o aumento (status 'rejeitado'), ofereça imediatamente uma análise financeira detalhada para recalcular o score. Se ele aceitar, apenas confirme e deixe que o sistema faça a transição automática.\n\n"
    "Regras de negócio:\n"
    "- Coerência de Limite: Se o score sugerir um limite (ex: R$ 2.000,00) menor do que o cliente já possui (ex: R$ 5.000,00), explique que para aumentar acima do valor atual será necessária uma nova análise.\n"
    "- Você já tem acesso aos dados do cliente autenticado; use-os para evitar perguntas redundantes.\n"
    "- Atenha-se estritamente a assuntos de limite de crédito. Formate valores como R$ X.XXX,XX.\n"
    "- Em caso de erros técnicos, utilize uma linguagem cordial e sugira alternativas sem expor logs internos."
)

tools = [consultar_limite, solicitar_aumento, verificar_score_limite, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_credito_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "credito"
    
    # Consolidamos todo o contexto dinâmico em uma única mensagem de sistema para evitar confusão no LLM
    contexto_agente = "Você é o assistente de CRÉDITO do Banco Ágil.\n"
    if state.get("cliente_autenticado"):
        nome = state.get("dados_cliente", {}).get("nome", "Cliente")
        cpf = state.get("cpf_cliente", "desconhecido")
        score = state.get("dados_cliente", {}).get("score_credito", "desconhecido")
        limite = state.get("dados_cliente", {}).get("limite_credito", "desconhecido")
        contexto_agente += f"- Cliente: {nome} (CPF: {cpf}, Score: {score}, Limite Atual: {limite})\n"
        
        if state.get("analise_realizada"):
            contexto_agente += "- STATUS: A análise financeira já foi concluída nesta sessão. NÃO ofereça nova análise.\n"
        else:
            contexto_agente += "- STATUS: O cliente pode solicitar análise financeira se o aumento for negado.\n"

    # Se for uma transferência, injetamos a instrução de início
    if transferencia:
        contexto_agente += "\nSua primeira tarefa agora é: APRESENTE O MENU DE CRÉDITO (1. Consultar limite, 2. Solicitar aumento) e cumprimente o cliente."
        messages = messages + [
            SystemMessage(content=contexto_agente),
            HumanMessage(content="Olá! Por favor, me mostre as opções de crédito.", name="system")
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
            msg.name = "credito"
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and "me mostre as opções de crédito" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "credito", "encerrado": encerrado}
