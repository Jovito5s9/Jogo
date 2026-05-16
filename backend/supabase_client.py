from supabase import create_client
from backend.config import load_config

config = load_config()

supabase = create_client(config["url"], config["key"])