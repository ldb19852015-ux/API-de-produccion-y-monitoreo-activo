import os

from dotenv import load_dotenv

load_dotenv()

def init_observability():
    # Configuración automática de trazas para LangSmith
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "Charcuteria-La-Merced-API")
