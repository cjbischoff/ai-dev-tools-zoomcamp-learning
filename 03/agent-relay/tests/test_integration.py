"""Integration test for the full Agent Relay task flow.

Tests the acceptance scenario from SPEC.md:
Register two agents -> send a task -> claim -> complete -> verify result.
"""

import os

os.environ.setdefault("RELAY_DATABASE_URL", "sqlite:////tmp/agent-relay-integration-test.db")

import pytest
from fastapi.testclient import TestClient

import main
from database import Base, engine


@pytest.fixture(autouse=True)
def empty_database():
    """Fresh database per test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(main.app) as c:
        yield c


def register(client, name):
    resp = client.post("/api/v1/agents", json={"name": name})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data, {"Authorization": f"Bearer {data['token']}"}


class TestTaskFlow:
    """Full acceptance scenario: register two agents and exchange a task."""

    def test_register_and_exchange_task(self, client):
        # Register two agents
        alice_data, alice_auth = register(client, "alice")
        bob_data, bob_auth = register(client, "uppercase")

        alice_id = alice_data["agent_id"]
        bob_id = bob_data["agent_id"]

        # Alice sends a task to Bob
        send_resp = client.post(
            "/api/v1/tasks",
            json={"to": bob_id, "input": "hello world"},
            headers=alice_auth,
        )
        assert send_resp.status_code == 201
        send_body = send_resp.json()
        assert send_body["status"] == "queued"
        task_id = send_body["task_id"]

        # Bob claims the task
        claim_resp = client.post(
            "/api/v1/tasks/claim",
            json={"worker_id": "test-laptop", "wait_seconds": 5},
            headers=bob_auth,
        )
        assert claim_resp.status_code == 200
        claim_body = claim_resp.json()
        assert claim_body["task_id"] == task_id
        assert claim_body["from"] == alice_id
        assert claim_body["input"] == "hello world"
        claim_token = claim_body["claim_token"]

        # Bob completes the task
        complete_resp = client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={"claim_token": claim_token, "output": "HELLO WORLD"},
            headers=bob_auth,
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"

        # Alice checks the result
        alice_result = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=alice_auth,
        )
        assert alice_result.status_code == 200
        body = alice_result.json()
        assert body["status"] == "completed"
        assert body["output"] == "HELLO WORLD"
        assert body["from"] == alice_id
        assert body["to"] == bob_id
        assert body["task_id"] == task_id

    def test_unauthenticated_rejected(self, client):
        """Unauthenticated requests to task endpoints return 401."""
        resp = client.post("/api/v1/tasks", json={"to": "agent_x", "input": "test"})
        assert resp.status_code == 401

        resp = client.post("/api/v1/tasks/claim", json={"wait_seconds": 1})
        assert resp.status_code == 401

        resp = client.get("/api/v1/tasks/task_000")
        assert resp.status_code == 401
