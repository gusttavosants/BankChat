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
    "- O processo de autenticação deve ser feito em duas etapas rigorosas: primeiro, peça o CPF e use a ferramenta 'verificar_cpf'. Somente se o CPF for validado, peça a data de nascimento e use 'autenticar_cliente'.\n"
    "- Se o CPF ou a data estiverem incorretos, informe o erro de forma educada e mencione quantas tentativas o cliente ainda possui (o limite total é de 3 falhas antes do encerramento automático).\n"
    "- Após a autenticação bem-sucedida, cumprimente o cliente pelo nome e ofereça o menu principal: 1. Câmbio ou 2. Crédito.\n"
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
    messages = state["messages"]
    transferencia = state.get("agente_atual") != "triagem"
    tentativas = state.get("tentativas_auth", 0)
    
    # Injeta contexto de tentativas e CPF (apenas instrução, o texto final é do LLM)
    ctx_auth = ""
    if tentativas > 0:
        ctx_auth = f"INSTRUÇÃO DE SEGURANÇA: O cliente já falhou {tentativas} vezes. Informe que ele tem mais {3 - tentativas} tentativas restantes."
    
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
            
            # Detecta sucesso/falha no CPF
            if tool_name == 'verificar_cpf':
                import json
                try:
                    res_data = json.loads(m.content)
                    if res_data.get("status_code") == 200:
                        # Extrai o CPF da chamada da ferramenta (reversed logic)
                        for prev_msg in reversed(all_res_messages):
                            if hasattr(prev_msg, "tool_calls"):
                                for tc in prev_msg.tool_calls:
                                    if tc["id"] == m.tool_call_id:
                                        cpf_cliente = tc["args"].get("cpf")
                                        break
                            if cpf_cliente: break
                    else:
                        tentativas += 1
                        cpf_cliente = None # Limpa se falhou
                except: pass

            # Detecta sucesso/falha na autenticação completa
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
            new_messages.append(AIMessage(content="Limite de tentativas excedido. Por segurança, este atendimento será encerrado.", name="triagem"))

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
