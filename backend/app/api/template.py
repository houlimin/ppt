from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.database import get_async_db
from app.schemas import TemplateResponse, PaginatedResponse
from app.services.template_service import TemplateService, UserTemplateService
from app.core.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/templates", tags=["模板"])


class CreateTemplateRequest(BaseModel):
    name: str
    category: str
    description: str
    template_data: dict
    thumbnail_url: Optional[str] = None


class UpdateTemplateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    template_data: Optional[dict] = None
    thumbnail_url: Optional[str] = None


@router.get("", response_model=PaginatedResponse)
async def get_templates(
    category: Optional[str] = Query(None),
    is_premium: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    service = TemplateService(db)
    templates, total = await service.get_templates(category, is_premium, page, page_size)
    
    return PaginatedResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0
    )


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_async_db)):
    service = TemplateService(db)
    return await service.get_categories()


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    service = TemplateService(db)
    template = await service.get_template_by_id(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )
    
    return TemplateResponse.model_validate(template)


@router.post("", response_model=TemplateResponse)
async def create_template(
    request: CreateTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    service = UserTemplateService(db)
    template = await service.create_user_template(
        user_id=current_user.id,
        name=request.name,
        category=request.category,
        description=request.description,
        template_data=request.template_data,
        thumbnail_url=request.thumbnail_url
    )
    return TemplateResponse.model_validate(template)


@router.post("/upload-thumbnail")
async def upload_template_thumbnail(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    from app.services.storage_service import LocalStorageService
    import io
    
    storage = LocalStorageService()
    content = await file.read()
    thumbnail_url = await storage.upload_bytes(
        content,
        folder="template_thumbnails",
        filename=f"user_{current_user.id}_{file.filename}"
    )
    
    return {"thumbnail_url": thumbnail_url}


@router.get("/user/my", response_model=PaginatedResponse)
async def get_my_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    service = UserTemplateService(db)
    templates, total = await service.get_user_templates(current_user.id, page, page_size)
    
    return PaginatedResponse(
        items=[TemplateResponse.model_validate(t) for t in templates],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: UpdateTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    service = UserTemplateService(db)
    template = await service.update_user_template(
        template_id=template_id,
        user_id=current_user.id,
        **request.model_dump(exclude_unset=True)
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权限修改"
        )
    
    return TemplateResponse.model_validate(template)


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    service = UserTemplateService(db)
    success = await service.delete_user_template(template_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或无权限删除"
        )
    
    return {"message": "删除成功"}
