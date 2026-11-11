import os


def init_observability():
    # Configuración de trazas para observabilidad (LangSmith)
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "Charcuteria-La-Merced-API")