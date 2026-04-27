from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

def trim_messages(messages: list, last_n: int = 15) -> list:
    """
    Mantém as últimas N mensagens, preservando a lógica de contexto, 
    a primeira mensagem de sistema e a integridade de sequências de ToolCalls.
    """
    if len(messages) <= last_n:
        return messages
    
    start_index = len(messages) - last_n
    
    # Regra de Integridade: Nunca começar com uma ToolMessage. 
    # Se começarmos com uma, precisamos recuar até encontrar a AIMessage que a gerou.
    while start_index > 0 and isinstance(messages[start_index], ToolMessage):
        start_index -= 1
        
    # Garante que se pegarmos a ToolMessage, pegamos também o seu AIMessage pai (com tool_calls)
    if start_index > 0 and isinstance(messages[start_index], AIMessage) and hasattr(messages[start_index], "tool_calls"):
        # Se a mensagem anterior for um HumanMessage, talvez queiramos incluí-la também para contexto
        pass

    trimmed = messages[start_index:]
    
    # Garante que a primeira mensagem de sistema (geralmente o prompt principal) seja mantida
    if isinstance(messages[0], SystemMessage) and messages[0] not in trimmed:
        trimmed.insert(0, messages[0])
            
    return trimmed
