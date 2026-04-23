from langgraph.prebuilt import create_react_agent
from config import LLM
from tools.credito_tools import consultar_limite, solicitar_aumento, verificar_score_limite
from tools.encerramento_tools import encerrar_atendimento
from state import BancoAgilState
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage

system_prompt = (
    "Você é o assistente virtual do Banco Ágil especializado em Crédito.\n\n"
    "OBJETIVO: Auxiliar na consulta de limite e permitir a solicitação de aumento de crédito.\n\n"
    "OPÇÕES DISPONÍVEIS (APRESENTE ESTE MENU AO INICIAR):\n"
    "1. Consultar seu limite atual;\n"
    "2. Solicitar aumento de limite.\n\n"
    "RESPONSABILIDADES:\n"
    "1. Consultar o limite disponível (PADRÃO: R$ X.XXX,XX).\n"
    "   - Após informar o limite, pergunte se o cliente deseja: 1. Consultar Câmbio ou 2. Finalizar o Atendimento.\n"
    "2. Solicitar aumento de limite:\n"
    "   - Peça o novo valor desejado.\n"
    "   - Use 'solicitar_aumento' para gerar o pedido formal (CSV).\n"
    "   - Se o status retornado for 'rejeitado', informe o cliente e ofereça realizar uma análise financeira detalhada agora mesmo para tentar recalcular o score.\n"
    "   - IMPORTANTE: Se o cliente ACEITAR a análise (disser 'sim', 'quero', etc.), APENAS confirme a ação (ex: 'Excelente! Vamos iniciar a análise agora mesmo...') e encerre sua resposta. NÃO peça renda ou qualquer outro dado financeiro, pois o sistema fará a transferência para o setor responsável automaticamente.\n"
    "   - Se o cliente NÃO desejar a análise, ofereça: 1. Consultar Câmbio ou 2. Finalizar o Atendimento.\n\n"
    "REGRAS CRÍTICAS (MÁXIMA PRIORIDADE):\n"
    "1. LÓGICA DE COERÊNCIA DE LIMITE: NUNCA diga que o 'limite máximo permitido' é um valor INFERIOR ao que o cliente já possui. Se o sistema retornar que o limite para o score é R$ 2.000,00, mas o cliente já tem R$ 5.000,00, você deve dizer: 'Como você já possui um limite de R$ 5.000,00 (que é superior ao sugerido pelo seu score atual), para conseguirmos qualquer aumento acima deste valor, precisamos realizar uma nova análise financeira.'\n"
    "2. VOCÊ JÁ TEM ACESSO AO SCORE DO CLIENTE NO CONTEXTO. NUNCA pergunte o score se ele já estiver autenticado.\n"
    "3. NUNCA ofereça 'contratar' ou 'simular empréstimo'. Atenha-se às opções de limite.\n"
    "4. NÃO tente 'vender' o limite pré-aprovado. Apenas apresente as opções de serviço.\n"
    "5. Formate valores monetários sempre no padrão brasileiro: R$ X.XXX,XX.\n\n"
    "TRATAMENTO DE ERROS TÉCNICOS:\n"
    "1. Se uma ferramenta retornar status 500 ou erro desconhecido, informe: 'Desculpe, tive um problema técnico ao acessar seus dados de limite. Podemos tentar novamente em instantes ou você pode consultar o Câmbio enquanto isso.'\n"
    "2. Se a API de crédito estiver lenta ou indisponível, peça desculpas e ofereça alternativas.\n"
    "3. NUNCA mostre logs técnicos."
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
