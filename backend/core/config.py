import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv(override=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")

def get_llm():
    if LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.2)
    elif LLM_PROVIDER == "openrouter":
        return ChatOpenAI(
            model_name=MODEL_NAME, 
            temperature=0.2, 
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1"
        )
    else:
        return ChatGroq(model_name=MODEL_NAME, temperature=0.2)

LLM = get_llm()
