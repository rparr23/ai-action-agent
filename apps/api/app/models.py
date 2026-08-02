from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PLANNING = "planning"
    RESEARCHING = "researching"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"


class ActionType(StrEnum):
    EMAIL = "send_email"
    TICKET = "create_ticket"
    MEETING = "schedule_meeting"


class TaskRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=4000)
    action_type: ActionType = ActionType.EMAIL


class Source(BaseModel):
    title: str
    url: str
    excerpt: str


class ProposedAction(BaseModel):
    type: ActionType
    arguments: dict[str, Any]
    risk: str = "medium"
    fingerprint: str


class TraceEvent(BaseModel):
    timestamp: str
    event: str
    detail: str
    status: str = "completed"


class Task(BaseModel):
    id: str
    prompt: str
    status: TaskStatus
    plan: list[str]
    summary: str
    sources: list[Source]
    proposed_action: ProposedAction | None = None
    trace: list[TraceEvent] = []
    result: dict[str, Any] | None = None


class DecisionRequest(BaseModel):
    fingerprint: str
