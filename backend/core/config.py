import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Carrega variáveis do .env
load_dotenv(find_dotenv())

def get_llm():
    """Retorna a instância do LLM configurada no .env."""
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    MODEL_NAME = os.getenv("MODEL_NAME")
    
    if LLM_PROVIDER == "groq":
        return ChatGroq(
            model=MODEL_NAME, 
            temperature=0.0, 
            api_key=os.getenv("GROQ_API_KEY")
        )
    elif LLM_PROVIDER == "google":
        return ChatGoogleGenerativeAI(
            model=MODEL_NAME, 
            temperature=0.0
        )
    elif LLM_PROVIDER == "openrouter":
        return ChatOpenAI(
            model=MODEL_NAME, 
            temperature=0.0, 
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
    else: # default openai
        return ChatOpenAI(
            model=MODEL_NAME, 
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

LLM = get_llm()
