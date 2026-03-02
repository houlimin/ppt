import pytest
from httpx import AsyncClient


class TestAuth:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == test_user.username
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestUser:
    @pytest.mark.asyncio
    async def test_get_profile(self, client: AsyncClient, auth_headers):
        response = await client.get(
            "/api/v1/user/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/user/profile")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, auth_headers):
        response = await client.put(
            "/api/v1/user/profile",
            headers=auth_headers,
            json={
                "nickname": "New Nickname",
                "profession": "Developer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "New Nickname"
        assert data["profession"] == "Developer"
    
    @pytest.mark.asyncio
    async def test_get_membership(self, client: AsyncClient, auth_headers):
        response = await client.get(
            "/api/v1/user/membership",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "membership_type" in data
        assert "is_member" in data
