from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.score_tools import calcular_score, atualizar_score
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente do Banco Ágil. Seu objetivo é realizar uma análise financeira para o score.\n\n"
    "COLETA (UMA POR VEZ):\n"
    "1. Renda mensal bruta.\n"
    "2. Tipo de emprego (formal/CLT, autônomo ou desempregado).\n"
    "3. Despesas fixas mensais.\n"
    "4. Número de dependentes.\n"
    "5. Dívidas ativas (Sim/Não).\n\n"
    "PROCESSO:\n"
    "- Após coletar tudo, use 'calcular_score' e depois 'atualizar_score'.\n"
    "- Informe o NOVO SCORE e o NOVO LIMITE ao cliente.\n"
    "- Finalize avisando que o sistema retornará para as opções de crédito."
)

tools = [calcular_score, atualizar_score, consultar_limite, solicitar_aumento, verificar_score_limite, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_entrevista_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "entrevista"
    
    if transferencia:
        contexto = "Inicie a análise financeira. Cliente autenticado."
        if state.get("cliente_autenticado"):
            cli = state.get("dados_cliente", {})
            contexto += f" Cliente: {cli.get('nome')} | Score: {cli.get('score_credito')}"
            
        messages = messages + [
            SystemMessage(content=contexto),
            HumanMessage(content="[TRANSFERÊNCIA RECEBIDA]", name="system"),
        ]
    
    response = agent.invoke({"messages": messages})
    all_res_messages = response["messages"]
    new_messages = all_res_messages[len(messages):]
    
    encerrado = state.get("encerrado", False)
    dados_cliente = state.get("dados_cliente", {})

    for m in new_messages:
        if isinstance(m, ToolMessage):
            tool_name = None
            for prev_msg in reversed(all_res_messages):
                if hasattr(prev_msg, "tool_calls") and prev_msg.tool_calls:
                    for tc in prev_msg.tool_calls:
                        if tc["id"] == m.tool_call_id:
                            tool_name = tc["name"]
                            break
                if tool_name: break

            if tool_name == 'encerrar_atendimento' or '"encerrado": true' in m.content.lower():
                encerrado = True

            if tool_name == 'atualizar_score':
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        data = res_data.get("data")
                        if data:
                            if data.get("score_novo") is not None:
                                dados_cliente["score_credito"] = data.get("score_novo")
                            if data.get("limite_novo") is not None:
                                dados_cliente["limite_credito"] = data.get("limite_novo")
                except: pass
    
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "entrevista"
            
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "[TRANSFERÊNCIA RECEBIDA]"
        )]
            
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
