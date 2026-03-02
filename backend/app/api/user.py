from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_async_db
from app.models import User
from app.schemas import UserResponse, UserUpdate, MessageResponse
from app.core import get_current_user

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    if update_data.nickname is not None:
        current_user.nickname = update_data.nickname
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
    if update_data.profession is not None:
        current_user.profession = update_data.profession
    if update_data.industry is not None:
        current_user.industry = update_data.industry
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/membership")
async def get_membership(
    current_user: User = Depends(get_current_user)
):
    return {
        "membership_type": current_user.membership_type,
        "membership_expire_at": current_user.membership_expire_at,
        "is_member": current_user.is_member,
        "credits": current_user.credits,
        "storage_used": current_user.storage_used
    }


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    current_user.is_active = False
    await db.commit()
    
    return MessageResponse(message="账号已注销", success=True)
