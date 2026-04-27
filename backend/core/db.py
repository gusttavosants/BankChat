import os
from dotenv import load_dotenv

# Carrega variáveis do .env (como chaves de API do LLM)
load_dotenv()

# Na branch Streamlit, não utilizamos o Supabase por padrão, focando em persistência CSV local.
# Se precisar reativar, as chaves SUPABASE_URL e SUPABASE_KEY devem ser configuradas no .env.
