import os
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env para o ambiente

def load_config():
    load_dotenv()
    data = {
    "key" : os.getenv("SUPABASE_ANON_KEY"),
    "url" : os.getenv("SUPABASE_URL")
    }
    return data