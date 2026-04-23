from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.score_tools import calcular_score, atualizar_score
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o consultor financeiro do Banco Ágil. Seu papel agora é conduzir uma análise para recalcular o score de crédito do cliente.\n\n"
    "Princípios de atendimento:\n"
    "- Mantenha a continuidade da conversa; para o cliente, você é o mesmo assistente único que já o estava atendendo.\n"
    "- Inicie com uma frase natural de apoio e passe para a coleta de dados.\n"
    "- Solicite as seguintes informações, sempre uma por vez e nesta ordem: 1. Renda mensal bruta, 2. Tipo de emprego (formal/CLT, autônomo ou desempregado), 3. Despesas fixas mensais, 4. Número de dependentes e 5. Se possui dívidas ativas.\n\n"
    "Fluxo de processamento:\n"
    "- Assim que coletar todos os 5 dados, utilize a ferramenta 'calcular_score'.\n"
    "- Em seguida, use 'atualizar_score' para gravar os novos valores no sistema.\n"
    "- Com a confirmação da atualização, informe ao cliente seu novo score e o novo limite de crédito sugerido.\n"
    "- Finalize o atendimento de forma cordial, avisando que o sistema o redirecionará para as opções de crédito.\n\n"
    "Observações:\n"
    "- Não informe valores fictícios; use sempre o retorno das ferramentas.\n"
    "- Formate todos os valores monetários no padrão R$ X.XXX,XX."
)

tools = [calcular_score, atualizar_score, consultar_limite, solicitar_aumento, verificar_score_limite, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_entrevista_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "entrevista"
    
    if transferencia:
        prompt_transferencia = "Você acaba de assumir este atendimento no contexto de ENTREVISTA FINANCEIRA. Explique que coletará dados para recalcular o score de forma natural."
        
        # Injeta contexto de autenticação se disponível
        if state.get("cliente_autenticado"):
            nome = state.get("dados_cliente", {}).get("nome", "Cliente")
            cpf = state.get("cpf_cliente", "desconhecido")
            score = state.get("dados_cliente", {}).get("score_credito", "desconhecido")
            prompt_transferencia += f" O cliente já está autenticado como {nome} (CPF: {cpf}, Score atual: {score}). NÃO peça CPF ou dados básicos."
            
        # Injeta system + mensagem gatilho para forçar apresentação imediata
        messages = messages + [
            SystemMessage(content=prompt_transferencia),
            HumanMessage(content="[TRANSFERÊNCIA RECEBIDA]", name="system"),
        ]
    
    response = agent.invoke({"messages": messages})
    all_res_messages = response["messages"]
    new_messages = all_res_messages[len(messages):]
    
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
            
    # Remove a mensagem gatilho do retorno para não poluir o histórico da UI
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "[TRANSFERÊNCIA RECEBIDA]"
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
