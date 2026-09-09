import pytest
from app.dependencies import get_db


class TestCreateBoard:
    def test_create_board(self, authed_client):
        resp = authed_client.post("/api/boards", json={"name": "My Board"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "My Board"
        assert "id" in body
        assert "owner_id" in body

    def test_create_board_no_name(self, authed_client):
        resp = authed_client.post("/api/boards", json={})
        assert resp.status_code == 422

    def test_create_board_empty_name(self, authed_client):
        resp = authed_client.post("/api/boards", json={"name": ""})
        assert resp.status_code == 422

    def test_create_board_unauthenticated(self, client):
        resp = client.post("/api/boards", json={"name": "No Auth"})
        assert resp.status_code == 401


class TestListBoards:
    def test_list_boards(self, authed_client):
        authed_client.post("/api/boards", json={"name": "Board A"})
        authed_client.post("/api/boards", json={"name": "Board B"})

        resp = authed_client.get("/api/boards")
        assert resp.status_code == 200
        boards = resp.json()
        assert len(boards) == 2
        names = [b["name"] for b in boards]
        assert "Board A" in names
        assert "Board B" in names

    def test_list_boards_unauthenticated(self, client):
        resp = client.get("/api/boards")
        assert resp.status_code == 401


class TestGetBoard:
    def test_get_board_detail(self, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "Detail Test"})
        board_id = create_resp.json()["id"]

        # Create a card on the board
        authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo",
            "title": "Test Card",
        })

        resp = authed_client.get(f"/api/boards/{board_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Detail Test"
        assert "members" in body
        assert "cards" in body
        assert len(body["cards"]) == 1
        assert body["cards"][0]["title"] == "Test Card"

    def test_get_board_not_member(self, client, authed_client):
        # Create board as testuser
        create_resp = authed_client.post("/api/boards", json={"name": "Secret"})
        board_id = create_resp.json()["id"]

        # Register and login second user
        client.post("/api/auth/register", json={
            "username": "other",
            "password": "pass123",
        })

        # Second user should get 403 — not a member
        resp = client.get(f"/api/boards/{board_id}")
        assert resp.status_code == 403

    def test_get_board_not_found(self, authed_client):
        resp = authed_client.get("/api/boards/99999")
        assert resp.status_code == 404


class TestRenameBoard:
    def test_rename_board(self, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "Old Name"})
        board_id = create_resp.json()["id"]

        resp = authed_client.put(f"/api/boards/{board_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_rename_board_not_found(self, authed_client):
        resp = authed_client.put("/api/boards/99999", json={"name": "Ghost"})
        assert resp.status_code == 404


class TestDeleteBoard:
    def test_delete_board(self, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "To Delete"})
        board_id = create_resp.json()["id"]

        resp = authed_client.delete(f"/api/boards/{board_id}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Board should be gone
        resp = authed_client.get("/api/boards")
        assert len(resp.json()) == 0

    def test_delete_board_not_owner(self, db, app, authed_client):
        """A member (not owner) cannot delete the board."""
        create_resp = authed_client.post("/api/boards", json={"name": "Owned"})
        board_id = create_resp.json()["id"]

        from starlette.testclient import TestClient
        app.dependency_overrides[get_db] = lambda: db

        # Register member1 in a separate client so authed_client stays as testuser
        with TestClient(app) as other:
            other.post("/api/auth/register", json={
                "username": "member1",
                "password": "pass123",
            })

        # Invite member1 as owner (authed_client is still testuser)
        resp = authed_client.post(f"/api/boards/{board_id}/members", json={
            "username": "member1",
        })
        assert resp.status_code == 200

        # Try to delete as member1
        with TestClient(app) as other2:
            other2.post("/api/auth/login", json={
                "username": "member1",
                "password": "pass123",
            })
            resp = other2.delete(f"/api/boards/{board_id}")
            assert resp.status_code == 403


class TestMembers:
    def test_invite_member(self, db, app, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "Team Board"})
        board_id = create_resp.json()["id"]

        from starlette.testclient import TestClient
        app.dependency_overrides[get_db] = lambda: db

        # Register invitee in a separate client so authed_client keeps testuser session
        with TestClient(app) as other:
            other.post("/api/auth/register", json={
                "username": "invitee",
                "password": "pass123",
            })

        resp = authed_client.post(f"/api/boards/{board_id}/members", json={
            "username": "invitee",
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Board detail should show 2 members
        detail = authed_client.get(f"/api/boards/{board_id}").json()
        assert len(detail["members"]) == 2

    def test_invite_nonexistent_user(self, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "Test"})
        board_id = create_resp.json()["id"]

        resp = authed_client.post(f"/api/boards/{board_id}/members", json={
            "username": "ghost",
        })
        assert resp.status_code == 404

    def test_remove_member(self, db, app, authed_client):
        create_resp = authed_client.post("/api/boards", json={"name": "Test"})
        board_id = create_resp.json()["id"]

        from starlette.testclient import TestClient
        app.dependency_overrides[get_db] = lambda: db

        with TestClient(app) as other:
            other.post("/api/auth/register", json={
                "username": "removeme",
                "password": "pass123",
            })

        authed_client.post(f"/api/boards/{board_id}/members", json={
            "username": "removeme",
        })

        detail = authed_client.get(f"/api/boards/{board_id}").json()
        target = [m for m in detail["members"] if m["username"] == "removeme"][0]

        resp = authed_client.delete(f"/api/boards/{board_id}/members/{target['user_id']}")
        assert resp.status_code == 200

        detail_after = authed_client.get(f"/api/boards/{board_id}").json()
        assert len(detail_after["members"]) == 1  # Only owner left
