from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.auth_tools import autenticar_cliente, verificar_cpf
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você atua como o assistente virtual do Banco Ágil. Seu papel é receber os clientes com cordialidade e realizar a autenticação de segurança antes de qualquer serviço.\n\n"
    "Orientações de atendimento:\n"
    "- Comece sempre com uma saudação calorosa e boas-vindas ao Banco Ágil. Explique que, por segurança, você precisa confirmar alguns dados antes de prosseguir.\n"
    "- O processo de segurança é rigoroso e possui apenas 3 tentativas NO TOTAL (contando erros de CPF e Data). Após a 3ª falha, o atendimento será encerrado automaticamente.\n"
    "- Siga sempre estas duas etapas: 1. Peça o CPF e valide com 'verificar_cpf'. Somente após o sucesso, 2. Peça a data de nascimento e valide com 'autenticar_cliente'.\n"
    "- Se houver erro em qualquer etapa, informe o cliente e diga quantas tentativas ele ainda possui do total de 3.\n"
    "- Após a autenticação, cumprimente-o pelo nome e ofereça: 1. Câmbio ou 2. Crédito.\n"
    "- Caso o cliente selecione uma opção, apenas confirme a transição (ex: 'Perfeito, vou verificar as informações de Crédito...') e deixe que o especialista assuma.\n\n"
    "Diretrizes técnicas:\n"
    "- Nunca tente realizar consultas de limites ou cotações neste estágio de triagem.\n"
    "- Faça apenas uma pergunta por vez e nunca pule a etapa de validação do CPF.\n"
    "- Em caso de instabilidade nas ferramentas, peça desculpas e sugira tentar novamente em instantes, sem expor detalhes técnicos ou logs.\n"
    "- Mantenha a formatação de valores no padrão brasileiro (R$ X.XXX,XX)."
)

tools = [autenticar_cliente, verificar_cpf, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def agente_triagem_node(state: BancoAgilState):
    tentativas = state.get("tentativas_auth", 0)
    auth_sucesso = state.get("cliente_autenticado", False)
    
    # Bloqueio imediato se o limite já foi atingido em turnos anteriores
    if tentativas >= 3 and not auth_sucesso:
        return {
            "messages": [AIMessage(content="Limite de 3 tentativas excedido. O atendimento foi encerrado.", name="triagem")],
            "encerrado": True
        }

    messages = state["messages"]
    transferencia = state.get("agente_atual") != "triagem"
    
    # Injeta contexto de segurança para o LLM
    ctx_auth = ""
    if tentativas > 0:
        ctx_auth = f"SEGURANÇA: O cliente já falhou {tentativas} vezes. Ele tem apenas {3 - tentativas} tentativa(s) RESTANTE(S) do total de 3."
    
    cpf_validado = state.get("cpf_cliente")
    if cpf_validado:
        ctx_auth += f" CONTEXTO: O CPF {cpf_validado} já foi validado. Peça apenas a data de nascimento."
    
    current_messages = []
    if ctx_auth:
        current_messages.append(SystemMessage(content=ctx_auth))
    
    current_messages.extend(messages)

    if transferencia:
        prompt_transferencia = (
            "Você é o Atendimento Ágil. O cliente voltou para a triagem. "
            "Cumprimente-o cordialmente e ofereça o menu: 1. Câmbio, 2. Crédito."
        )
        current_messages = current_messages + [
            SystemMessage(content=prompt_transferencia),
            HumanMessage(content="[TRANSFERÊNCIA RECEBIDA]", name="system"),
        ]

    response = agent.invoke({"messages": current_messages})
    all_res_messages = response["messages"]
    # Remove o SystemMessage de contexto que injetamos no início para o cálculo de offset
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
            
            # Detecta falhas em ferramentas de autenticação
            if tool_name in ['verificar_cpf', 'autenticar_cliente']:
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        if tool_name == 'verificar_cpf':
                            # Extrai o CPF para o estado
                            for prev_msg in reversed(all_res_messages):
                                if hasattr(prev_msg, "tool_calls"):
                                    for tc in prev_msg.tool_calls:
                                        if tc["id"] == m.tool_call_id:
                                            cpf_cliente = tc["args"].get("cpf")
                                            break
                                if cpf_cliente: break
                        else: # autenticar_cliente
                            data = res_data.get("data")
                            if data:
                                auth_sucesso = True
                                dados_cliente = data
                                cpf_cliente = data.get("cpf")
                                tentativas = 0
                    else:
                        tentativas += 1
                except:
                    tentativas += 1 # Conta erro de parsing como tentativa falha por segurança

    if tentativas >= 3 and not auth_sucesso:
        encerrado = True
        # Limpa as mensagens do agente para evitar que ele peça os dados de novo no 3º erro
        new_messages = [m for m in new_messages if not isinstance(m, AIMessage)]
        new_messages.append(AIMessage(
            content="Limite de 3 tentativas excedido. Por segurança, este atendimento será encerrado agora. Por favor, tente novamente mais tarde.", 
            name="triagem"
        ))

    # Persiste o CPF no estado se ele foi validado nesta rodada ou já existia
    cpf_final = cpf_cliente or state.get("cpf_cliente")
    
    # Adiciona o nome do agente às mensagens para fins de UI
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
