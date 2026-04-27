from langgraph.prebuilt import create_react_agent
from core.config import LLM
from agents.triagem.tools import autenticar_cliente, verificar_cpf
from agents.shared.encerramento import encerrar_atendimento
from core.state import BancoAgilState
from core.prompts import apply_global_rules
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from utils.formatters import clean_llm_response

system_prompt = apply_global_rules(
    "Você atua como o assistente virtual do Banco Ágil. Seu papel é receber os clientes com cordialidade e realizar a autenticação de segurança antes de qualquer serviço.\n\n"
    "Orientações de atendimento:\n"
    "- Comece sempre com uma saudação calorosa e boas-vindas ao Banco Ágil. Explique que, por segurança, você precisa confirmar alguns dados antes de prosseguir.\n"
    "- O processo de segurança é rigoroso e possui apenas 3 tentativas NO TOTAL. Após a 3ª falha, o atendimento será encerrado automaticamente.\n"
    "- Siga sempre estas duas etapas: 1. Peça o CPF e valide com 'verificar_cpf'. Somente após o sucesso, 2. Peça a data de nascimento e valide com 'autenticar_cliente'.\n"
    "- OBRIGATÓRIO: Chame 'verificar_cpf' toda vez que o cliente fornecer um CPF.\n"
    "- Após a autenticação bem-sucedida, cumprimente-o pelo nome e ofereça o menu: '1. Câmbio ou 2. Crédito'.\n"
    "- Caso o cliente selecione uma opção, apenas confirme a transição e deixe que o especialista assuma.\n\n"
    "Diretrizes técnicas:\n"
    "- Nunca tente realizar consultas de limites ou cotações neste estágio.\n"
    "- Faça apenas uma pergunta por vez e nunca pule a etapa de validação do CPF.\n"
    "- Em caso de instabilidade, peça desculpas e sugira tentar novamente em instantes."
)

tools = [autenticar_cliente, verificar_cpf, encerrar_atendimento]
agent = create_react_agent(LLM, tools=tools, prompt=system_prompt)

def _safe_msg(text: str) -> str:
    if not text: return text
    return text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "--").replace("\u201d", '"').replace("\u201c", '"').replace("\u2019", "'").replace("\u2018", "'")

def agente_triagem_node(state: BancoAgilState):
    tentativas = state.get("tentativas_auth", 0)
    auth_sucesso = state.get("cliente_autenticado", False)
    
    # Bloqueio imediato se o limite já foi atingido em turnos anteriores
    if tentativas >= 3 and not auth_sucesso:
        return {
            "messages": [AIMessage(content=_safe_msg("Limite de 3 tentativas excedido. O atendimento foi encerrado."), name="triagem")],
            "encerrado": True
        }

    messages = state["messages"]
    transferencia = state.get("agente_atual") != "triagem"
    
    ctx_auth = ""
    if tentativas > 0:
        ctx_auth = f"INSTRUÇÃO INTERNA E SECRETA DO SISTEMA (NÃO REPITA ESSE TEXTO PARA O USUÁRIO): O cliente já falhou {tentativas} vezes. Ele tem apenas {3 - tentativas} tentativa(s) RESTANTE(S) do total de 3."
    
    cpf_validado = state.get("cpf_cliente")
    if cpf_validado:
        ctx_auth += f" O CPF {cpf_validado} já foi validado. Peça apenas a data de nascimento, mas avise sobre as tentativas restantes se houver."
    
    current_messages = list(messages)
    if ctx_auth:
        current_messages.append(SystemMessage(content=ctx_auth))

    if transferencia:
        prompt_transferencia = (
            "Você é o Atendimento Ágil. O cliente voltou para a triagem. "
            "Ofereça o menu: 1. Câmbio, 2. Crédito. IMPORTANTE: Não se apresente novamente nem dê boas-vindas, apenas forneça as opções de forma direta."
        )
        current_messages = current_messages + [
            SystemMessage(content=prompt_transferencia),
            HumanMessage(content="[MUDANÇA DE CONTEXTO: VOLTAR PARA TRIAGEM]", name="system"),
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
            tool_name = m.name

            if tool_name == 'encerrar_atendimento' or '"encerrado": true' in m.content.lower():
                encerrado = True
            
            # Detecção de falhas de autenticação (CPF ou Data)
            is_auth_tool = tool_name in ['verificar_cpf', 'autenticar_cliente']
            if is_auth_tool:
                import json
                try:
                    res_data = json.loads(m.content)
                    status = res_data.get("status_code")
                    
                    if status == 200:
                        if tool_name == 'verificar_cpf':
                            # Busca o CPF nos argumentos da chamada correspondente
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
                        # Qualquer status diferente de 200 (401, 404, 500) conta como tentativa
                        tentativas += 1
                except Exception as e:
                    # Falha no processamento do retorno também conta como erro de segurança
                    tentativas += 1

    if tentativas >= 3 and not auth_sucesso:
        encerrado = True
        # Limpa as mensagens do agente para evitar que ele peça os dados de novo no 3º erro
        new_messages = [m for m in new_messages if not isinstance(m, AIMessage)]
        new_messages.append(AIMessage(
            content=_safe_msg("Limite de 3 tentativas excedido. Por segurança, este atendimento será encerrado agora. Por favor, tente novamente mais tarde."), 
            name="triagem"
        ))

    # Persiste o CPF no estado se ele foi validado nesta rodada ou já existia
    cpf_final = cpf_cliente or state.get("cpf_cliente")
    
    # Adiciona o nome do agente e sanitiza as mensagens para fins de UI e segurança
    for msg in new_messages:
        if isinstance(msg, AIMessage):
            msg.name = "triagem"
            msg.content = clean_llm_response(_safe_msg(msg.content))
            
    if transferencia:
        new_messages = [m for m in new_messages if not (
            isinstance(m, HumanMessage) and m.content == "[MUDANÇA DE CONTEXTO: VOLTAR PARA TRIAGEM]"
        )]
            
    if tentativas >= 3 and not auth_sucesso:
        encerrado = True

    return {
        "messages": new_messages, 
        "agente_atual": "triagem", 
        "encerrado": encerrado,
        "cliente_autenticado": auth_sucesso or state.get("cliente_autenticado"),
        "dados_cliente": dados_cliente,
        "cpf_cliente": cpf_final,
        "tentativas_auth": tentativas
    }
