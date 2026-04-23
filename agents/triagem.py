from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.auth_tools import autenticar_cliente, verificar_cpf
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente virtual do Banco Ágil. Sua missão é acolher o cliente e autenticá-lo.\n\n"
    "FLUXO:\n"
    "1. Saudação calorosa e pedido de CPF.\n"
    "2. Após validar o CPF (verificar_cpf), peça a DATA DE NASCIMENTO (autenticar_cliente).\n"
    "3. O cliente tem 3 tentativas no total.\n"
    "4. Após autenticado, apresente o menu: 1. Câmbio, 2. Crédito.\n\n"
    "REGRAS:\n"
    "- Uma pergunta por vez.\n"
    "- Formate valores monetários como R$ X.XXX,XX.\n"
    "- Trate erros técnicos de forma cordial, sem expor logs."
)

tools = [autenticar_cliente, verificar_cpf, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_triagem_node(state: BancoAgilState):
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "triagem"
    tentativas = state.get("tentativas_auth", 0)
    
    ctx_auth = ""
    if tentativas > 0:
        ctx_auth = f"Segurança: {tentativas}/3 tentativas. Informe o restante."
    
    cpf_validado = state.get("cpf_cliente")
    if cpf_validado:
        ctx_auth += f" CPF {cpf_validado} validado. Peça data de nascimento."
    
    current_messages = [SystemMessage(content=ctx_auth)] if ctx_auth else []
    current_messages.extend(messages)

    if transferencia:
        prompt_transferencia = "Atendimento Ágil: O cliente voltou para a triagem. Ofereça: 1. Câmbio, 2. Crédito."
        current_messages = current_messages + [
            SystemMessage(content=prompt_transferencia),
            HumanMessage(content="[TRANSFERÊNCIA RECEBIDA]", name="system"),
        ]

    response = agent.invoke({"messages": current_messages})
    all_res_messages = response["messages"]
    new_messages = all_res_messages[len(current_messages):]
    
    encerrado = state.get("encerrado", False)
    auth_sucesso = False
    dados_cliente = state.get("dados_cliente")
    cpf_cliente = state.get("cpf_cliente")
    
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
            
            if tool_name == 'verificar_cpf':
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        for prev_msg in reversed(all_res_messages):
                            if hasattr(prev_msg, "tool_calls"):
                                for tc in prev_msg.tool_calls:
                                    if tc["id"] == m.tool_call_id:
                                        cpf_cliente = tc["args"].get("cpf")
                                        break
                            if cpf_cliente: break
                    else:
                        tentativas += 1
                        cpf_cliente = None
                except: pass

            if tool_name == 'autenticar_cliente':
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        data = res_data.get("data")
                        if data:
                            auth_sucesso = True
                            dados_cliente = data
                            cpf_cliente = data.get("cpf")
                            tentativas = 0 
                    else:
                        tentativas += 1
                except: pass

    if tentativas >= 3 and not auth_sucesso:
        encerrado = True
        if not any("encerrar" in msg.content.lower() for msg in new_messages if isinstance(msg, AIMessage)):
            new_messages.append(AIMessage(content="Limite de tentativas excedido. Atendimento encerrado.", name="triagem"))

    cpf_final = cpf_cliente or state.get("cpf_cliente")
    
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "triagem"
            
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "[TRANSFERÊNCIA RECEBIDA]"
        )]
            
    return {
        "messages": new_messages, 
        "agente_atual": "triagem", 
        "encerrado": encerrado,
        "cliente_autenticado": auth_sucesso or state.get("cliente_autenticado"),
        "dados_cliente": dados_cliente,
        "cpf_cliente": cpf_final,
        "tentativas_auth": tentativas
    }
