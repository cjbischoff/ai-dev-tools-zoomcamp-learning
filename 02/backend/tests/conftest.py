import pytest
from starlette.testclient import TestClient

from app.dependencies import get_db
from app.sql_database import SqlDatabaseService


@pytest.fixture
def db():
    """Fresh in-memory SQLite database per test."""
    return SqlDatabaseService(db_url="sqlite:///:memory:")


@pytest.fixture
def app(db):
    """FastAPI app with overridden DB dependency."""
    from app.main import app as _app

    _app.dependency_overrides[get_db] = lambda: db
    yield _app
    _app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def registered_user(client):
    """Register a default test user. Returns the client with session cookie set."""
    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "test123",
    })
    assert resp.status_code == 200, resp.text
    return resp


@pytest.fixture
def authed_client(client, registered_user):
    """Client with an active session (cookies managed automatically)."""
    return client
