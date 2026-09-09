import pytest


@pytest.fixture
def board_id(authed_client):
    """Create a board and return its id."""
    resp = authed_client.post("/api/boards", json={"name": "Test Board"})
    return resp.json()["id"]


class TestCreateCard:
    def test_create_card(self, authed_client, board_id):
        resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo",
            "title": "New Task",
            "description": "Do the thing",
            "assignee": "alice",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "New Task"
        assert body["column"] == "todo"
        assert body["description"] == "Do the thing"
        assert body["assignee"] == "alice"
        assert body["position"] == 1

    def test_create_card_with_due_date(self, authed_client, board_id):
        resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "in_progress",
            "title": "Due task",
            "due_date": "2026-09-20",
        })
        assert resp.status_code == 201
        assert resp.json()["due_date"] == "2026-09-20"

    def test_create_card_no_title(self, authed_client, board_id):
        resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo",
            "title": "",
        })
        assert resp.status_code == 422

    def test_create_card_invalid_column(self, authed_client, board_id):
        resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "invalid",
            "title": "Bad column",
        })
        assert resp.status_code == 422

    def test_create_card_increments_position(self, authed_client, board_id):
        authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "First",
        })
        resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "Second",
        })
        assert resp.json()["position"] == 2


class TestUpdateCard:
    def test_update_card_title(self, authed_client, board_id):
        create_resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "Original",
        })
        card_id = create_resp.json()["id"]

        resp = authed_client.put(f"/api/cards/{card_id}", json={
            "title": "Updated",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_update_card_all_fields(self, authed_client, board_id):
        create_resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "Orig",
        })
        card_id = create_resp.json()["id"]

        resp = authed_client.put(f"/api/cards/{card_id}", json={
            "title": "New",
            "description": "Desc",
            "due_date": "2026-10-01",
            "assignee": "bob",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "New"
        assert body["description"] == "Desc"
        assert body["due_date"] == "2026-10-01"
        assert body["assignee"] == "bob"

    def test_update_card_not_found(self, authed_client):
        resp = authed_client.put("/api/cards/99999", json={"title": "Ghost"})
        assert resp.status_code == 404


class TestDeleteCard:
    def test_delete_card(self, authed_client, board_id):
        create_resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "Delete me",
        })
        card_id = create_resp.json()["id"]

        resp = authed_client.delete(f"/api/cards/{card_id}")
        assert resp.status_code == 200

        # Board should have 0 cards
        board = authed_client.get(f"/api/boards/{board_id}").json()
        assert len(board["cards"]) == 0

    def test_delete_card_not_found(self, authed_client):
        resp = authed_client.delete("/api/cards/99999")
        assert resp.status_code == 404


class TestMoveCard:
    def test_move_card_between_columns(self, authed_client, board_id):
        create = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "Movable",
        })
        card_id = create.json()["id"]

        resp = authed_client.patch(f"/api/cards/{card_id}/move", json={
            "new_column": "in_progress",
            "new_position": 1,
        })
        assert resp.status_code == 200
        assert resp.json()["column"] == "in_progress"

    def test_move_card_multiple_positions(self, authed_client, board_id):
        # Create 3 cards in todo
        c1 = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "A",
        }).json()
        authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "B",
        }).json()
        c3 = authed_client.post(f"/api/boards/{board_id}/cards", json={
            "column": "todo", "title": "C",
        }).json()

        # Move card C to position 1 (top)
        resp = authed_client.patch(f"/api/cards/{c3['id']}/move", json={
            "new_column": "todo",
            "new_position": 1,
        })
        assert resp.status_code == 200

        # Verify order: C should be position 1, A position 2, B position 3
        board = authed_client.get(f"/api/boards/{board_id}").json()
        todo_cards = [c for c in board["cards"] if c["column"] == "todo"]
        todo_cards.sort(key=lambda c: c["position"])
        titles = [c["title"] for c in todo_cards]
        assert titles == ["C", "A", "B"]


class TestReorderCards:
    def test_reorder_within_column(self, authed_client, board_id):
        # Create 3 cards
        ids = []
        for title in ["First", "Second", "Third"]:
            resp = authed_client.post(f"/api/boards/{board_id}/cards", json={
                "column": "todo", "title": title,
            })
            ids.append(resp.json()["id"])

        # Reverse the order
        reversed_ids = list(reversed(ids))
        resp = authed_client.patch(f"/api/boards/{board_id}/reorder", json={
            "column": "todo",
            "card_ids": reversed_ids,
        })
        assert resp.status_code == 200

        # Verify
        board = authed_client.get(f"/api/boards/{board_id}").json()
        todo_cards = sorted(
            [c for c in board["cards"] if c["column"] == "todo"],
            key=lambda c: c["position"],
        )
        titles = [c["title"] for c in todo_cards]
        assert titles == ["Third", "Second", "First"]
