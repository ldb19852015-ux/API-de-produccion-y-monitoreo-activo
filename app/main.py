import os
import uuid

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel
from redis import Redis

from app.graph import build_agent_graph
from app.worker import run_background_task

load_dotenv()

app = FastAPI(title="API Multi-Agente - Charcutería La Merced", version="1.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = Redis.from_url(REDIS_URL)
agent_graph = build_agent_graph()

class TaskRequest(BaseModel):
    task: str

class ApprovalRequest(BaseModel):
    approved: bool

@app.post("/tasks/")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Registrar estado inicial PENDING en Redis
    redis_client.hset(f"job:{job_id}", mapping={"status": "PENDING", "task": request.task})
    
    # Encolar la tarea en segundo plano sin bloquear el event loop
    background_tasks.add_task(run_background_task, job_id, request.task)
    
    return {
        "job_id": job_id,
        "status": "PENDING",
        "message": "Tarea encolada correctamente en segundo plano."
    }

@app.get("/tasks/{job_id}")
async def get_task_status(job_id: str):
    job_data = redis_client.hgetall(f"job:{job_id}")
    if not job_data:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")
    return {k.decode("utf-8"): v.decode("utf-8") for k, v in job_data.items()}

@app.post("/tasks/{job_id}/approve")
async def approve_task(job_id: str, approval: ApprovalRequest):
    config = {"configurable": {"thread_id": job_id}}
    try:
        # Reanudar la ejecución del grafo usando Command
        result = agent_graph.invoke(
            Command(resume={"approved": approval.approved}),
            config
        )
        redis_client.hset(f"job:{job_id}", mapping={"status": "DONE", "result": str(result)})
        return {"job_id": job_id, "status": "DONE", "result": result}
    except Exception as e:  # noqa: BLE001
        redis_client.hset(f"job:{job_id}", mapping={"status": "FAILED", "error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))
