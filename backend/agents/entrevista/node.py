from langgraph.prebuilt import create_react_agent
from core.config import LLM
from agents.entrevista.tools import calcular_score, atualizar_score
from agents.credito.tools import consultar_limite, solicitar_aumento, verificar_score_limite
from agents.shared.encerramento import encerrar_atendimento
from core.state import BancoAgilState
from core.prompts import apply_global_rules
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from utils.formatters import clean_llm_response
from utils.context_manager import trim_messages

system_prompt = apply_global_rules(
    "Você é o consultor financeiro do Banco Ágil. Seu papel é coletar dados para recalcular o score de crédito.\n\n"
    "ORDEM DAS PERGUNTAS (Estritamente uma por vez):\n"
    "1. Renda mensal bruta\n"
    "2. Tipo de emprego (formal/CLT, autônomo ou desempregado)\n"
    "3. Despesas fixas mensais\n"
    "4. Número de dependentes\n"
    "5. Se possui dívidas ativas\n\n"
    "REGRAS DE OURO:\n"
    "- Se esta for a sua PRIMEIRA resposta na análise, sua saída deve ser EXATAMENTE: 'Para iniciarmos a análise, qual é a sua renda mensal bruta?'\n"
    "- Nunca pergunte duas coisas ao mesmo tempo. Responda apenas uma pergunta por vez.\n"
    "- Use a ferramenta 'calcular_score' somente após coletar TODOS os dados solicitados acima."
)

tools = [calcular_score, atualizar_score, solicitar_aumento, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_entrevista_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "entrevista"
    
    if transferencia:
        prompt_transferencia = "Você acaba de assumir este atendimento para realizar uma ANÁLISE FINANCEIRA (ENTREVISTA). Siga as instruções de coleta de dados do seu prompt de sistema. IMPORTANTE: Não se apresente novamente nem dê boas-vindas."
        
        # Injeta contexto de autenticação se disponível
        if state.get("cliente_autenticado"):
            nome = state.get("dados_cliente", {}).get("nome", "Cliente")
            cpf = state.get("cpf_cliente", "desconhecido")
            score = state.get("dados_cliente", {}).get("score_credito", "desconhecido")
            limite = state.get("dados_cliente", {}).get("limite_credito", "desconhecido")
            prompt_transferencia += f" O cliente já está autenticado como {nome} (CPF: {cpf}, Score atual: {score}, Limite atual: {limite}). NÃO peça CPF ou dados básicos."
            
        # Injeta system + mensagem gatilho para forçar apresentação imediata
        messages = messages + [
            SystemMessage(content=prompt_transferencia),
            HumanMessage(content="Inicie a coleta de dados."),
        ]
    
    # Otimiza o histórico enviado para a LLM
    trimmed_messages = trim_messages(messages, last_n=15)
    
    response = agent.invoke({"messages": trimmed_messages})
    all_res_messages = response["messages"]
    new_messages = all_res_messages[len(trimmed_messages):]
    
    # Verifica se a ferramenta de encerramento foi chamada
    encerrado = state.get("encerrado", False)
    dados_cliente = state.get("dados_cliente", {})

    for m in new_messages:
        if isinstance(m, ToolMessage):
            # Detecta o nome da ferramenta de forma robusta
            tool_name = None
            for prev_msg in reversed(all_res_messages):
                if hasattr(prev_msg, "tool_calls") and prev_msg.tool_calls:
                    for tc in prev_msg.tool_calls:
                        if tc["id"] == m.tool_call_id:
                            tool_name = tc["name"]
                            break
                if tool_name: break

            # Detecta encerramento
            if tool_name == 'encerrar_atendimento' or '"encerrado": true' in m.content.lower():
                encerrado = True

            # Captura atualização de score para refletir no estado global
            if tool_name == 'atualizar_score':
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        data = res_data.get("data")
                        if data:
                            novo_score = data.get("score_novo")
                            novo_limite = data.get("limite_novo")
                            if novo_score is not None:
                                dados_cliente["score_credito"] = novo_score
                            if novo_limite is not None:
                                dados_cliente["limite_credito"] = novo_limite
                except:
                    pass
    
    # Adiciona o nome do agente às mensagens para fins de UI
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "entrevista"
            msg.content = clean_llm_response(msg.content)
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "Inicie a coleta de dados."
        )]
            
    # Captura se a análise foi concluída com sucesso para evitar loops infinitos
    analise_concluida = state.get("analise_realizada", False)
    for m in new_messages:
        if isinstance(m, ToolMessage) and '"status_code": 200' in m.content and "score_novo" in m.content:
            analise_concluida = True

    return {
        "messages": new_messages, 
        "agente_atual": "entrevista", 
        "encerrado": encerrado, 
        "dados_cliente": dados_cliente,
        "analise_realizada": analise_concluida
    }
