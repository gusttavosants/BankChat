from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def trim_messages(messages: list, last_n: int = 10) -> list:
    """Mantém as últimas N mensagens, preservando a lógica de contexto e a primeira mensagem de sistema se houver."""
    if len(messages) <= last_n:
        return messages
    
    # Preserva as últimas N mensagens
    trimmed = messages[-last_n:]
    
    # Garante que a primeira mensagem de sistema (geralmente o prompt principal) seja mantida se estiver presente no início
    if isinstance(messages[0], SystemMessage):
        if messages[0] not in trimmed:
            trimmed.insert(0, messages[0])
            
    return trimmed
