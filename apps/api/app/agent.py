from datetime import UTC, datetime
from uuid import uuid4

from .config import Settings
from .models import ActionType, ProposedAction, Source, Task, TaskRequest, TaskStatus, TraceEvent
from .research import search, summarize
from .safety import action_fingerprint


def event(name: str, detail: str, status: str = "completed") -> TraceEvent:
    return TraceEvent(
        timestamp=datetime.now(UTC).isoformat(), event=name, detail=detail, status=status
    )


def action_args(kind: ActionType, summary: str) -> dict:
    if kind == ActionType.TICKET:
        return {
            "project": "AI-GOV",
            "title": "Review enterprise AI governance risks",
            "description": summary,
            "priority": "medium",
        }
    if kind == ActionType.MEETING:
        return {
            "attendees": ["leadership@example.com"],
            "title": "AI governance risk review",
            "starts_at": "2026-08-05T14:00:00-04:00",
            "duration_minutes": 30,
        }
    return {
        "to": ["leadership@example.com"],
        "subject": "Enterprise AI governance: findings and next steps",
        "body": f"Leadership team,\n\n{summary}\n\nRecommended next step: assign owners and prioritize a documented AI risk review.\n\nRegards,\nAI Action Agent",
    }


async def run_task(request: TaskRequest, settings: Settings) -> Task:
    plan = [
        "Understand goal and constraints",
        "Plan research strategy",
        "Search trusted web sources",
        "Synthesize cited findings",
        "Draft proposed action",
        "Pause for human approval",
    ]
    task = Task(
        id=str(uuid4()),
        prompt=request.prompt,
        status=TaskStatus.RESEARCHING,
        plan=plan,
        summary="",
        sources=[],
        trace=[event("planning", "Created a six-step plan")],
    )
    if "web_search" not in settings.tools:
        task.status = TaskStatus.FAILED
        task.trace.append(event("safe_fallback", "Web search is disabled", "failed"))
        return task
    sources: list[Source] = await search(request.prompt, settings)
    task.sources = sources
    task.summary = summarize(sources)
    task.trace.extend(
        [
            event("research", f"Collected {len(sources)} cited sources"),
            event("synthesis", "Produced an evidence-backed summary"),
        ]
    )
    if not sources:
        task.status = TaskStatus.FAILED
        task.trace.append(
            event("safe_fallback", "Stopped because evidence was insufficient", "failed")
        )
        return task
    args = action_args(request.action_type, task.summary)
    fp = action_fingerprint(request.action_type, args)
    task.proposed_action = ProposedAction(type=request.action_type, arguments=args, fingerprint=fp)
    task.status = TaskStatus.AWAITING_APPROVAL
    task.trace.extend(
        [
            event("draft", f"Prepared {request.action_type} action"),
            event(
                "approval_required",
                "External action is blocked pending an exact-match approval",
                "pending",
            ),
        ]
    )
    return task
