"""Integration tests for API endpoints."""

import pytest


class TestHealthEndpoint:
    def test_health_check(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestRootEndpoint:
    def test_root_returns_info(self, client):
        res = client.get("/")
        assert res.status_code == 200


class TestAuthEndpoints:
    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "pass123",
            "full_name": "New User"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "newuser"
        assert "id" in data
    
    def test_register_duplicate(self, client):
        client.post("/api/auth/register", json={
            "username": "dupuser", "password": "pass123"
        })
        res = client.post("/api/auth/register", json={
            "username": "dupuser", "password": "pass456"
        })
        assert res.status_code == 400
    
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser", "password": "pass123"
        })
        res = client.post("/api/auth/login", data={
            "username": "loginuser", "password": "pass123"
        })
        assert res.status_code == 200
        assert "access_token" in res.json()
    
    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser2", "password": "pass123"
        })
        res = client.post("/api/auth/login", data={
            "username": "loginuser2", "password": "wrongpass"
        })
        assert res.status_code == 401


class TestExtractionEndpoint:
    def test_extract_no_file(self, client):
        res = client.post("/api/extract")
        assert res.status_code == 422  # Missing file
    
    def test_extract_invalid_doc_type(self, client):
        # Create a minimal 1x1 PNG
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (100, 100), "white").save(buf, format="PNG")
        buf.seek(0)
        
        res = client.post(
            "/api/extract?document_type=invalid_type",
            files={"file": ("test.png", buf, "image/png")}
        )
        assert res.status_code == 400


class TestVerifyEndpoint:
    def test_verify_missing_extraction(self, client):
        res = client.post("/api/verify", json={
            "extraction_id": "nonexistent",
            "form_data": {"name": "test"}
        })
        assert res.status_code == 404


class TestRetrievalEndpoints:
    def test_get_extraction_not_found(self, client):
        res = client.get("/api/extraction/nonexistent")
        assert res.status_code == 404
    
    def test_get_verification_not_found(self, client):
        res = client.get("/api/verification/nonexistent")
        assert res.status_code == 404
