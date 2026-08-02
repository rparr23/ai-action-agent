from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def create(kind="send_email"):
    r = client.post(
        "/tasks",
        json={
            "prompt": "Research enterprise AI governance risks and prepare a leadership action",
            "action_type": kind,
        },
    )
    assert r.status_code == 201
    return r.json()


def test_research_has_citations():
    task = create()
    assert len(task["sources"]) >= 3
    assert all(s["url"].startswith("https://") for s in task["sources"])


def test_action_blocks_before_approval():
    task = create()
    assert task["status"] == "awaiting_approval"
    assert task["result"] is None


def test_approval_requires_exact_fingerprint():
    task = create()
    r = client.post(f"/tasks/{task['id']}/approve", json={"fingerprint": "tampered"})
    assert r.status_code == 409


def test_approved_mock_action_executes_once():
    task = create("create_ticket")
    payload = {"fingerprint": task["proposed_action"]["fingerprint"]}
    assert client.post(f"/tasks/{task['id']}/approve", json=payload).status_code == 200
    assert client.post(f"/tasks/{task['id']}/approve", json=payload).status_code == 409


def test_rejected_action_never_executes():
    task = create("schedule_meeting")
    payload = {"fingerprint": task["proposed_action"]["fingerprint"]}
    r = client.post(f"/tasks/{task['id']}/reject", json=payload)
    assert r.json()["status"] == "rejected"
    assert client.post(f"/tasks/{task['id']}/approve", json=payload).status_code == 409
