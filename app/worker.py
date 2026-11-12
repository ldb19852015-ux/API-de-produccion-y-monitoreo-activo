import os

from dotenv import load_dotenv
from redis import Redis

from app.graph import build_agent_graph

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = Redis.from_url(REDIS_URL)

def run_background_task(job_id: str, task_text: str):
    # Actualizar estado a RUNNING en Redis
    redis_client.hset(f"job:{job_id}", mapping={"status": "RUNNING", "task": task_text})
    
    try:
        graph = build_agent_graph()
        config = {"configurable": {"thread_id": job_id}}
        
        result = graph.invoke({"task": task_text}, config)
        
        # Verificar si el grafo se detuvo por interrupción (HITL) o finalizó
        state_snapshot = graph.get_state(config)
        if state_snapshot.next:
            redis_client.hset(f"job:{job_id}", mapping={"status": "SUSPENDED_FOR_APPROVAL"})
        else:
            redis_client.hset(f"job:{job_id}", mapping={"status": "DONE", "result": str(result)})
            
    except Exception as e:  # noqa: BLE001
        # Ante cualquier fallo, el estado pasa a FAILED para evitar polling infinito
        redis_client.hset(f"job:{job_id}", mapping={"status": "FAILED", "error": str(e)})
