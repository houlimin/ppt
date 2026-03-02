from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MembershipTypeEnum(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ProjectStatusEnum(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class InputTypeEnum(str, Enum):
    TEXT = "text"
    OUTLINE = "outline"
    DOCUMENT = "document"


class AIModelEnum(str, Enum):
    QWEN = "qwen"
    KIMI = "kimi"


class TemplateCategoryEnum(str, Enum):
    BUSINESS = "business"
    EDUCATION = "education"
    CREATIVE = "creative"
    INDUSTRY = "industry"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    profession: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=50)


class UserResponse(UserBase):
    id: int
    nickname: Optional[str]
    avatar_url: Optional[str]
    profession: Optional[str]
    industry: Optional[str]
    membership_type: str
    membership_expire_at: Optional[datetime]
    credits: int
    storage_used: int
    is_member: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PPTPageContent(BaseModel):
    page_index: int
    title: str
    content: List[str]
    layout_type: str = "single_column"
    notes: Optional[str] = None


class PPTContentJSON(BaseModel):
    title: str
    pages: List[PPTPageContent]
    theme: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class PPTGenerateByText(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000)
    template_id: Optional[int] = None
    ai_model: AIModelEnum = AIModelEnum.QWEN
    page_count: Optional[int] = Field(None, ge=1, le=50)


class PPTGenerateByOutline(BaseModel):
    title: str = Field(..., max_length=200)
    outline: List[Dict[str, Any]]
    template_id: Optional[int] = None
    ai_model: AIModelEnum = AIModelEnum.QWEN


class PPTProjectCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    template_id: Optional[int] = None
    content_json: Dict[str, Any]


class PPTProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    status: Optional[ProjectStatusEnum] = None


class PPTProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    template_id: Optional[int]
    content_json: Dict[str, Any]
    thumbnail_url: Optional[str]
    page_count: int
    file_url: Optional[str]
    file_size: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    description: Optional[str]
    thumbnail_url: Optional[str]
    preview_images: Optional[List[str]]
    is_premium: bool
    is_system: bool
    creator_id: Optional[int]
    download_count: int
    rating: float
    template_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_type: str
    payment_method: str


class OrderResponse(BaseModel):
    id: int
    order_no: str
    product_type: str
    amount: float
    payment_method: Optional[str]
    payment_status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class GenerationStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: Optional[str]
    result: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
