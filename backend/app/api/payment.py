from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import uuid
from app.database import get_async_db
from app.models import User, Order
from app.schemas import OrderCreate, OrderResponse, MessageResponse
from app.core import get_current_user
from app.config import settings

router = APIRouter(prefix="/payment", tags=["支付"])


def generate_order_no() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = uuid.uuid4().hex[:8].upper()
    return f"PPT{timestamp}{random_str}"


def get_membership_duration(product_type: str) -> timedelta:
    durations = {
        "monthly": timedelta(days=30),
        "quarterly": timedelta(days=90),
        "yearly": timedelta(days=365)
    }
    return durations.get(product_type, timedelta(days=30))


def get_membership_price(product_type: str) -> float:
    prices = {
        "monthly": settings.MONTHLY_MEMBERSHIP_PRICE,
        "quarterly": settings.QUARTERLY_MEMBERSHIP_PRICE,
        "yearly": settings.YEARLY_MEMBERSHIP_PRICE
    }
    return prices.get(product_type, 0)


@router.post("/create", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    amount = get_membership_price(order_data.product_type)
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的产品类型"
        )
    
    order = Order(
        user_id=current_user.id,
        order_no=generate_order_no(),
        product_type=order_data.product_type,
        amount=amount,
        payment_method=order_data.payment_method
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return OrderResponse.model_validate(order)


@router.post("/callback")
async def payment_callback(
    order_no: str,
    payment_status: str,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Order).where(Order.order_no == order_no)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if payment_status == "paid":
        order.payment_status = "paid"
        order.paid_at = datetime.now()
        
        result = await db.execute(
            select(User).where(User.id == order.user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            duration = get_membership_duration(order.product_type)
            
            if user.membership_expire_at and user.membership_expire_at > datetime.now():
                user.membership_expire_at += duration
            else:
                user.membership_expire_at = datetime.now() + duration
            
            user.membership_type = order.product_type
    
    await db.commit()
    
    return {"message": "回调处理成功", "success": True}


@router.get("/orders")
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/products")
async def get_products():
    return [
        {
            "type": "monthly",
            "name": "月度会员",
            "price": settings.MONTHLY_MEMBERSHIP_PRICE,
            "description": "30天会员权益"
        },
        {
            "type": "quarterly",
            "name": "季度会员",
            "price": settings.QUARTERLY_MEMBERSHIP_PRICE,
            "original_price": settings.MONTHLY_MEMBERSHIP_PRICE * 3,
            "discount": "17%",
            "description": "90天会员权益"
        },
        {
            "type": "yearly",
            "name": "年度会员",
            "price": settings.YEARLY_MEMBERSHIP_PRICE,
            "original_price": settings.MONTHLY_MEMBERSHIP_PRICE * 12,
            "discount": "36%",
            "description": "365天会员权益"
        }
    ]
