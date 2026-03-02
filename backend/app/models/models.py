from sqlalchemy import Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MembershipType(str, enum.Enum):
    FREE = "free"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    nickname = Column(String(50), nullable=True)
    profession = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    membership_type = Column(String(20), default="free")
    membership_expire_at = Column(DateTime, nullable=True)
    credits = Column(Integer, default=0)
    storage_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    projects = relationship("PPTProject", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    generation_history = relationship("GenerationHistory", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_member(self) -> bool:
        from datetime import datetime
        if self.membership_type == "free":
            return False
        if self.membership_expire_at and self.membership_expire_at > datetime.now():
            return True
        return False


class PPTProject(Base):
    __tablename__ = "ppt_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    content_json = Column(JSON, nullable=False, default=dict)
    thumbnail_url = Column(String(500), nullable=True)
    page_count = Column(Integer, default=0)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    status = Column(String(20), default="draft")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    template = relationship("Template", back_populates="projects")
    generation_history = relationship("GenerationHistory", back_populates="project")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    preview_images = Column(JSON, nullable=True)
    is_premium = Column(Boolean, default=False)
    is_system = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    download_count = Column(Integer, default=0)
    rating = Column(Numeric(2, 1), default=0.0)
    template_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    projects = relationship("PPTProject", back_populates="template")
    creator = relationship("User", foreign_keys=[creator_id])


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("ppt_projects.id", ondelete="SET NULL"), nullable=True)
    input_type = Column(String(20), nullable=False)
    input_content = Column(Text, nullable=True)
    ai_model = Column(String(50), nullable=True)
    generation_time = Column(Integer, nullable=True)
    status = Column(String(20), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="generation_history")
    project = relationship("PPTProject", back_populates="generation_history")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_no = Column(String(32), unique=True, nullable=False)
    product_type = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(20), nullable=True)
    payment_status = Column(String(20), default="pending")
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    usage_date = Column(DateTime, nullable=False)
    generation_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
