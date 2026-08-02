from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import event, run_task
from .config import get_settings
from .models import DecisionRequest, Task, TaskRequest, TaskStatus
from .safety import action_fingerprint, redact
from .store import store

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="AI Action Agent API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "mode": settings.agent_mode, "tools": sorted(settings.tools)}


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    return store.all()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    try:
        return store.get(task_id)
    except KeyError:
        raise HTTPException(404, "Task not found") from None


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(request: TaskRequest):
    try:
        task = await run_task(request, settings)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(503, str(exc)) from None
    store.save(task)
    return task


@app.post("/tasks/{task_id}/approve", response_model=Task)
def approve(task_id: str, decision: DecisionRequest):
    try:
        task = store.get(task_id)
    except KeyError:
        raise HTTPException(404, "Task not found") from None
    action = task.proposed_action
    if task.status != TaskStatus.AWAITING_APPROVAL or not action:
        raise HTTPException(409, "Task is not awaiting approval")
    current = action_fingerprint(action.type, action.arguments)
    if decision.fingerprint != current or action.fingerprint != current:
        raise HTTPException(409, "Action changed; review and approve the new exact action")
    if action.type not in settings.tools:
        raise HTTPException(403, "Action tool is disabled")
    if not store.claim(current):
        raise HTTPException(409, "This action has already been executed")
    task.status = TaskStatus.COMPLETED
    task.result = {
        "provider": "mock",
        "external_effect": False,
        "receipt": f"mock-{task.id[:8]}",
        "action": redact(action.arguments),
    }
    task.trace.append(event("executed", "Approved action executed through the mock adapter"))
    store.save(task)
    return task


@app.post("/tasks/{task_id}/reject", response_model=Task)
def reject(task_id: str, decision: DecisionRequest):
    try:
        task = store.get(task_id)
    except KeyError:
        raise HTTPException(404, "Task not found") from None
    if not task.proposed_action or decision.fingerprint != task.proposed_action.fingerprint:
        raise HTTPException(409, "Approval fingerprint mismatch")
    task.status = TaskStatus.REJECTED
    task.trace.append(event("rejected", "Human reviewer rejected the proposed action", "cancelled"))
    store.save(task)
    return task
