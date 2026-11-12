import os

from dotenv import load_dotenv
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt
from redis import Redis

from app.observability import init_observability

load_dotenv()
init_observability()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Inicializamos el cliente Redis y se lo pasamos explícitamente por keyword argument
redis_conn = Redis.from_url(REDIS_URL)
memory = RedisSaver(redis_client=redis_conn)
memory.setup()

def build_agent_graph():
    workflow = StateGraph(dict)

    def supervisor_node(state):
        task = state.get("task", "")
        return {"messages": [f"Supervisor procesando lote en Charcutería La Merced: {task}"]}

    # Nodo Human-in-the-Loop (HITL) que pausa la ejecución
    def hitl_approval_node(state):
        approval = interrupt({"question": "¿Aprueba la ejecución crítica de este lote en el secadero?"})
        if not approval.get("approved", False):
            raise ValueError("Operación rechazada y cancelada por el usuario.")
        return {"approved": True}

    def finalize_node(state):
        return {"result": "Lote procesado, curado y validado con éxito en el sistema."}

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("hitl_gate", hitl_approval_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "hitl_gate")
    workflow.add_edge("hitl_gate", "finalize")
    workflow.add_edge("finalize", END)

    graph = workflow.compile(checkpointer=memory)
    return graph
