import pytest
from httpx import AsyncClient
import json


class TestPPT:
    @pytest.mark.asyncio
    async def test_get_projects_empty(self, client: AsyncClient, auth_headers):
        response = await client.get(
            "/api/v1/ppt/projects",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    
    @pytest.mark.asyncio
    async def test_get_projects_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/v1/ppt/projects")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_project_via_text(
        self, 
        client: AsyncClient, 
        auth_headers,
        test_template,
        mocker
    ):
        mock_ai = mocker.patch("app.api.ppt.AIServiceFactory.get_service")
        mock_ai.return_value.generate_outline = pytest.AsyncMock(return_value={
            "title": "Test PPT",
            "pages": [{"page_index": 1, "title": "Page 1", "content": ["Point 1"]}]
        })
        mock_ai.return_value.expand_content = pytest.AsyncMock(return_value={
            "title": "Test PPT",
            "pages": [{"page_index": 1, "title": "Page 1", "content": ["Point 1"]}]
        })
        
        response = await client.post(
            "/api/v1/ppt/generate/text",
            headers=auth_headers,
            json={
                "description": "Create a test PPT about AI",
                "template_id": test_template.id,
                "ai_model": "qwen",
                "page_count": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "project_id" in data
    
    @pytest.mark.asyncio
    async def test_create_project_short_description(
        self,
        client: AsyncClient,
        auth_headers
    ):
        response = await client.post(
            "/api/v1/ppt/generate/text",
            headers=auth_headers,
            json={
                "description": "short",
                "ai_model": "qwen"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_project(
        self,
        client: AsyncClient,
        auth_headers,
        db_session,
        test_user
    ):
        project = {
            "user_id": test_user.id,
            "title": "Test Project",
            "content_json": {"title": "Test", "pages": []},
            "status": "draft"
        }
        from app.models import PPTProject
        ppt = PPTProject(**project)
        db_session.add(ppt)
        await db_session.commit()
        await db_session.refresh(ppt)
        
        response = await client.get(
            f"/api/v1/ppt/projects/{ppt.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Project"
    
    @pytest.mark.asyncio
    async def test_update_project(
        self,
        client: AsyncClient,
        auth_headers,
        db_session,
        test_user
    ):
        from app.models import PPTProject
        ppt = PPTProject(
            user_id=test_user.id,
            title="Original Title",
            content_json={"title": "Original", "pages": []},
            status="draft"
        )
        db_session.add(ppt)
        await db_session.commit()
        await db_session.refresh(ppt)
        
        response = await client.put(
            f"/api/v1/ppt/projects/{ppt.id}",
            headers=auth_headers,
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_delete_project(
        self,
        client: AsyncClient,
        auth_headers,
        db_session,
        test_user
    ):
        from app.models import PPTProject
        ppt = PPTProject(
            user_id=test_user.id,
            title="To Delete",
            content_json={"title": "Delete", "pages": []},
            status="draft"
        )
        db_session.add(ppt)
        await db_session.commit()
        await db_session.refresh(ppt)
        
        response = await client.delete(
            f"/api/v1/ppt/projects/{ppt.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestTemplates:
    @pytest.mark.asyncio
    async def test_get_templates(self, client: AsyncClient, test_template):
        response = await client.get("/api/v1/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_template_by_id(self, client: AsyncClient, test_template):
        response = await client.get(f"/api/v1/templates/{test_template.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_template.name
    
    @pytest.mark.asyncio
    async def test_get_template_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/templates/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_categories(self, client: AsyncClient):
        response = await client.get("/api/v1/templates/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0


class TestPayment:
    @pytest.mark.asyncio
    async def test_get_products(self, client: AsyncClient):
        response = await client.get("/api/v1/payment/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    @pytest.mark.asyncio
    async def test_create_order(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/payment/create",
            headers=auth_headers,
            json={
                "product_type": "monthly",
                "payment_method": "alipay"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "order_no" in data
        assert data["payment_status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_orders(self, client: AsyncClient, auth_headers):
        response = await client.get(
            "/api/v1/payment/orders",
            headers=auth_headers
        )
        assert response.status_code == 200
