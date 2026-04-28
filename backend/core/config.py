import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Carrega variáveis do .env
load_dotenv(find_dotenv())

def get_llm():
    """
    Retorna a instância do LLM configurada com suporte a fallbacks automáticos.
    Se o provedor principal falhar (503/500), tenta os secundários disponíveis.
    """
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    MODEL_NAME = os.getenv("MODEL_NAME")
    
    # Provedores Disponíveis para Fallback
    fallbacks = []
    
    # 1. Groq (Llama 3.1 8B - Rápido e Grátis)
    if os.getenv("GROQ_API_KEY"):
        fallbacks.append(ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, api_key=os.getenv("GROQ_API_KEY")))
    
    # 2. Google (Gemini 1.5 Flash - Estável)
    if os.getenv("GOOGLE_API_KEY"):
        fallbacks.append(ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0))

    # 3. OpenAI (GPT-4o mini - Confiável)
    if os.getenv("OPENAI_API_KEY"):
        fallbacks.append(ChatOpenAI(model="gpt-4o-mini", temperature=0.0, api_key=os.getenv("OPENAI_API_KEY")))

    # Configuração do Provedor Principal
    if LLM_PROVIDER == "groq":
        primary = ChatGroq(model=MODEL_NAME, temperature=0.0, api_key=os.getenv("GROQ_API_KEY"))
    elif LLM_PROVIDER == "google":
        primary = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.0)
    elif LLM_PROVIDER == "openrouter":
        primary = ChatOpenAI(
            model=MODEL_NAME, 
            temperature=0.0, 
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
    else: # default openai
        primary = ChatOpenAI(model=MODEL_NAME, temperature=0.0, api_key=os.getenv("OPENAI_API_KEY"))

    # Remove o próprio provedor principal da lista de fallbacks se ele estiver lá
    # (simplificação: apenas filtramos por classe/config se necessário, mas aqui a lista é fixa)
    
    if fallbacks:
        # Filtra para não repetir o mesmo provedor como fallback do principal (evita redundância inútil)
        # Por simplicidade, se houver fallbacks, aplicamos. LangChain gerencia a tentativa.
        return primary.with_fallbacks(fallbacks)
    
    return primary

LLM = get_llm()
