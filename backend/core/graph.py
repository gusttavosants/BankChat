from langgraph.graph import StateGraph, END
from core.state import BancoAgilState
from agents.triagem.node import agente_triagem_node
from agents.credito.node import agente_credito_node
from agents.entrevista.node import agente_entrevista_node
from agents.cambio.node import agente_cambio_node
from langchain_core.messages import AIMessage, HumanMessage

def define_entry_point(state: BancoAgilState):
    """Define por qual nó o grafo deve começar com base no agente atual."""
    return state.get("agente_atual", "triagem")

def router(state: BancoAgilState):
    messages = state.get("messages", [])
    if not messages:
        return "triagem"
    
    last_msg_obj = messages[-1]
    last_message = last_msg_obj.content.lower()
    agente_atual = state.get("agente_atual", "triagem")
    
    print(f"--- DEBUG ROUTER ---")
    print(f"Agente Atual: {agente_atual}")
    print(f"Última Mensagem: {last_message[:50]}...")
    
    # Se o estado já sinaliza encerramento (pela flag ou por palavras-chave na mensagem)
    if state.get("encerrado") or any(k in last_message for k in ["encerrar", "encerrado", "sair", "tchau"]):
        print("Decisão: END (Sinalizado para encerrar)")
        return END

    # Se a última mensagem é do assistente, verificamos se ele está transferindo
    # Caso contrário, encerramos o turno para esperar a resposta do usuário
    if isinstance(last_msg_obj, AIMessage):
        # DETECÇÃO DE MENU INICIAL: Se a IA está APENAS listando opções (1. Câmbio, 2. Crédito)
        # sem ter uma decisão clara de para onde ir, paramos para o usuário escolher.
        is_menu_inicial = ("1." in last_message and "2." in last_message) and agente_atual == "triagem"
        
        # Se for o menu inicial de boas-vindas, esperamos o usuário
        if is_menu_inicial:
             print("Decisão: END (Aguardando escolha no menu inicial)")
             return END

        # Transições Implícitas: Detectamos o assunto mencionado pela IA para mover o contexto
        # PRIORIDADE: Se a IA está fazendo uma pergunta (?), paramos para o usuário responder.
        # EXCEÇÃO: Se ela já confirmou que VAI transferir (ex: "Vou verificar...", "Com certeza!").
        
        possivel_transicao = False
        if any(k in last_message for k in ["entrevista", "análise", "analise", "recalcular score", "crédito", "credito", "limite", "câmbio", "cambio", "moeda", "cotação"]):
            possivel_transicao = True
            
        if "?" in last_message and possivel_transicao:
            # Só transiciona se houver afirmação de ação imediata
            if not any(k in last_message for k in ["vou", "vamos", "estou", "com certeza", "claro"]):
                print("Decisão: END (Aguardando resposta do usuário à pergunta)")
                return END

        # 1. ENTREVISTA (Entrada)
        if any(k in last_message for k in ["entrevista", "análise", "analise", "recalcular score"]) and agente_atual != "entrevista":
             print("Decisão: Transição Implícita para ENTREVISTA")
             return "entrevista"

        # 2. CREDITO (Entrada ou Retorno)
        # Se estamos em entrevista, só voltamos para crédito se a análise estiver "finalizada" ou tiver "novo score"
        if any(k in last_message for k in ["crédito", "credito", "limite"]) and agente_atual != "credito":
            if agente_atual == "entrevista":
                if any(k in last_message for k in ["novo score", "concluído", "concluido", "finalizado", "resultado"]):
                    print("Decisão: Retorno para CREDITO (Análise Concluída)")
                    return "credito"
                else:
                    print("Decisão: Mantendo em ENTREVISTA (Aguardando conclusão da análise)")
                    return "entrevista"
            else:
                print("Decisão: Transição Implícita para CREDITO")
                return "credito"
        
        # 3. CAMBIO
        if any(k in last_message for k in ["câmbio", "cambio", "moeda", "cotação"]) and agente_atual != "cambio":
            print("Decisão: Transição Implícita para CAMBIO")
            return "cambio"

        if any(k in last_message for k in ["triagem", "início", "ajudar com câmbio ou crédito"]) and agente_atual != "triagem":
            print("Decisão: Transição Implícita para TRIAGEM")
            return "triagem"
        
        # Se não houve transferência e a IA fez uma pergunta, paramos
        if "?" in last_message:
            print("Decisão: END (Aguardando resposta do usuário)")
            return END
            
        print("Decisão: END (Turno IA finalizado)")
        return END

    # Se a mensagem é do usuário (HumanMessage), decidimos para onde ir
    # SEGURANÇA: Só permitimos mudar de setor se o usuário já estiver autenticado
    is_autenticado = state.get("dados_cliente") is not None

    if isinstance(last_msg_obj, HumanMessage):
        print(f"--- DEBUG ROUTER (USER) ---")
        print(f"User Message: {last_message}")
        
        # 1. Lógica de confirmação contextual: Verificamos se o usuário está respondendo a uma proposta de transição
        for msg in reversed(messages[:-1]):
            if isinstance(msg, AIMessage):
                ia_msg = msg.content.lower()
                print(f"Analisando proposta anterior da IA: {ia_msg[:100]}...")
                
                # Se a IA propôs entrevista/análise
                keywords_entrevista = ["entrevista", "análise", "analise", "recalcular score", "confirmar alguns dados", "análise financeira"]
                if any(k in ia_msg for k in keywords_entrevista):
                    is_confirmacao = any(k in last_message for k in ["sim", "com certeza", "claro", "pode ser", "quero", "aceito", "ok", "vamos", "prosseguir"])
                    is_dado_direto = any(c.isdigit() for c in last_message) or (len(last_message.split()) <= 2 and any(c.isdigit() for c in last_message))
                    
                    print(f"Match ENTREVISTA? Confirmação: {is_confirmacao}, Dado Direto: {is_dado_direto}")
                    if is_confirmacao or is_dado_direto:
                        if is_autenticado:
                            if state.get("analise_realizada"):
                                print("Bloqueio: Análise já realizada nesta sessão. Mantendo no agente atual.")
                                return agente_atual
                            if agente_atual != "entrevista":
                                print(f"Decisão: Transição para ENTREVISTA")
                                return "entrevista"
                        else:
                            print("Bloqueio: Necessário autenticação para Entrevista")
                
                # Se a IA propôs crédito
                keywords_credito = ["crédito", "credito", "limite", "aumento"]
                if any(k in ia_msg for k in keywords_credito):
                    is_confirmacao = any(k in last_message for k in ["sim", "claro", "quero", "pode ser", "ok"])
                    is_opcao = last_message in ["1", "2"]
                    print(f"Match CREDITO? Confirmação: {is_confirmacao}, Opção: {is_opcao}")
                    if is_confirmacao or is_opcao:
                        if is_autenticado:
                            if agente_atual != "credito":
                                print("Decisão: Transição para CREDITO")
                                return "credito"
                        else:
                            print("Bloqueio: Necessário autenticação para Crédito")

                # Se a IA propôs câmbio
                keywords_cambio = ["câmbio", "cambio", "moeda", "cotação", "cotar"]
                if any(k in ia_msg for k in keywords_cambio):
                    is_confirmacao = any(k in last_message for k in ["sim", "claro", "quero", "ok"])
                    is_assunto = any(k in last_message for k in ["dólar", "euro", "cotar", "moeda"])
                    print(f"Match CAMBIO? Confirmação: {is_confirmacao}, Assunto: {is_assunto}")
                    if is_confirmacao or is_assunto:
                        if is_autenticado:
                            if agente_atual != "cambio":
                                print("Decisão: Transição para CAMBIO")
                                return "cambio"
                        else:
                            print("Bloqueio: Necessário autenticação para Câmbio")
                
                # Se achamos uma mensagem da IA, paramos de procurar (proposta mais recente)
                break

        # 2. Detecção por palavras-chave diretas na mensagem do usuário
        print("Checking direct keywords in User message...")
        if any(k in last_message for k in ["entrevista", "análise", "analise", "recalcular score"]):
            if is_autenticado: return "entrevista"
        if any(k in last_message for k in ["crédito", "credito", "limite"]):
            if is_autenticado: return "credito"
        if any(k in last_message for k in ["câmbio", "cambio", "moeda", "cotação"]):
            if is_autenticado: return "cambio"
        if any(k in last_message for k in ["triagem", "início", "voltar"]):
            return "triagem"

    print(f"Decisão Final: Mantendo em {agente_atual}")
    return agente_atual

# Constrói o grafo
workflow = StateGraph(BancoAgilState)

# Adiciona nós
workflow.add_node("triagem", agente_triagem_node)
workflow.add_node("credito", agente_credito_node)
workflow.add_node("entrevista", agente_entrevista_node)
workflow.add_node("cambio", agente_cambio_node)

# Mapeamento global de destinos (todas as arestas podem ir para qualquer lugar)
MAPA_DESTINOS = {
    "triagem": "triagem",
    "credito": "credito",
    "cambio": "cambio",
    "entrevista": "entrevista",
    END: END
}

# Define arestas e roteamento
workflow.set_conditional_entry_point(define_entry_point, MAPA_DESTINOS)

workflow.add_conditional_edges("triagem", router, MAPA_DESTINOS)
workflow.add_conditional_edges("credito", router, MAPA_DESTINOS)
workflow.add_conditional_edges("entrevista", router, MAPA_DESTINOS)
workflow.add_conditional_edges("cambio", router, MAPA_DESTINOS)

app_graph = workflow.compile()
