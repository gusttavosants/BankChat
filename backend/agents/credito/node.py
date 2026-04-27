from langgraph.prebuilt import create_react_agent
from core.config import LLM
from agents.credito.tools import consultar_limite, solicitar_aumento, verificar_score_limite
from agents.shared.encerramento import encerrar_atendimento
from core.state import BancoAgilState
from core.prompts import apply_global_rules
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from utils.formatters import clean_llm_response

system_prompt = apply_global_rules(
    "Você é o especialista em Crédito do Banco Ágil. Seu objetivo é ajudar o cliente a consultar seu limite atual ou solicitar um aumento.\n\n"
    "Procedimentos de atendimento:\n"
    "- Ao iniciar, apresente estritamente o menu: 1. Consultar limite atual, 2. Solicitar aumento de limite. NÃO inclua outras opções.\n"
    "- Para consultas de limite, informe o valor e ofereça as opções: solicitar aumento de limite, consultar o serviço de Câmbio ou encerrar o atendimento.\n"
    "- Se o cliente solicitar um aumento, peça o valor desejado e use 'solicitar_aumento'.\n"
    "- Caso o sistema negue o aumento, ofereça a análise financeira detalhada.\n\n"
    "Regras de negócio:\n"
    "- Coerência de Limite: O 'Limite Máximo Permitido' retornado pelas ferramentas já considera o maior valor possível para o perfil.\n"
    "- Você já tem acesso aos dados do cliente autenticado; use-os para evitar perguntas redundantes.\n"
    "- Atenha-se estritamente a assuntos de limite de crédito. Formate valores como R$ X.XXX,XX."
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
        if state.get("analise_realizada"):
             contexto_agente += "\nSua tarefa agora é: Retome a conversa após a análise financeira concluída. NÃO apresente o menu inicial de forma genérica. Reconheça que a análise foi feita e pergunte como prosseguir com as opções de crédito (consultar limite ou solicitar novo aumento)."
             trigger_msg = "Como posso prosseguir agora com meu crédito?"
        else:
            contexto_agente += "\nSua primeira tarefa agora é: APRESENTE O MENU DE CRÉDITO (1. Consultar limite, 2. Solicitar aumento). IMPORTANTE: Não se apresente novamente nem dê boas-vindas, apenas forneça as opções de forma direta e natural."
            trigger_msg = "Gostaria de ver as opções de crédito."
        
        messages = messages + [
            SystemMessage(content=contexto_agente),
            HumanMessage(content=trigger_msg, name="system")
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
            msg.content = clean_llm_response(msg.content)
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and "opções de crédito" in m.content.lower()
        )]
            
    return {"messages": new_messages, "agente_atual": "credito", "encerrado": encerrado}
