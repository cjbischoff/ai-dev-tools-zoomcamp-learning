class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "secret123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["user"]["username"] == "newuser"
        assert "id" in body["user"]

    def test_register_duplicate_username(self, client):
        client.post("/api/auth/register", json={
            "username": "dupuser",
            "password": "secret123",
        })
        resp = client.post("/api/auth/register", json={
            "username": "dupuser",
            "password": "other456",
        })
        assert resp.status_code == 409
        assert "detail" in resp.json()

    def test_register_short_username(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "ab",
            "password": "secret123",
        })
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "validuser",
            "password": "12345",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        # First register
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        # Then login
        resp = client.post("/api/auth/login", json={
            "username": "loginuser",
            "password": "mypassword",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["user"]["username"] == "loginuser"

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "user1",
            "password": "correctpw",
        })
        resp = client.post("/api/auth/login", json={
            "username": "user1",
            "password": "wrongpw",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "somepass",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, authed_client):
        resp = authed_client.get("/api/auth/me")
        assert resp.status_code == 200
        body = resp.json()
        assert body["user"]["username"] == "testuser"

    def test_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


class TestLogout:
    def test_logout(self, authed_client):
        resp = authed_client.post("/api/auth/logout")
        assert resp.status_code == 200
        # After logout, /me should return 401
        resp = authed_client.get("/api/auth/me")
        assert resp.status_code == 401
