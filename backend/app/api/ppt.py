from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, date
import uuid
import json
import io
import os
from urllib.parse import quote
from app.database import get_async_db
from app.models import User, PPTProject, Template, GenerationHistory, DailyUsage
from app.schemas import (
    PPTGenerateByText, PPTGenerateByOutline, PPTProjectCreate,
    PPTProjectUpdate, PPTProjectResponse, GenerationStatusResponse,
    MessageResponse, PaginatedResponse, AIModelEnum
)
from app.core import get_current_user, get_optional_user
from app.services import AIServiceFactory, PPTGenerator, generate_ppt, get_storage_service, TemplateService
from app.services.storage_service import LocalStorageService
from app.config import settings

router = APIRouter(prefix="/ppt", tags=["PPT生成"])

generation_tasks = {}


async def check_daily_limit(user: User, db: AsyncSession) -> bool:
    if user.is_member:
        return True
    
    today = date.today()
    result = await db.execute(
        select(DailyUsage).where(
            DailyUsage.user_id == user.id,
            DailyUsage.usage_date == today
        )
    )
    usage = result.scalar_one_or_none()
    
    if usage and usage.generation_count >= settings.FREE_USER_DAILY_LIMIT:
        return False
    return True


async def increment_daily_usage(user: User, db: AsyncSession):
    today = date.today()
    result = await db.execute(
        select(DailyUsage).where(
            DailyUsage.user_id == user.id,
            DailyUsage.usage_date == today
        )
    )
    usage = result.scalar_one_or_none()
    
    if usage:
        usage.generation_count += 1
    else:
        usage = DailyUsage(
            user_id=user.id,
            usage_date=today,
            generation_count=1
        )
        db.add(usage)
    
    await db.commit()


def generate_ppt_task(
    task_id: str,
    user_id: int,
    project_id: int,
    content_json: dict,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    import asyncio
    asyncio.run(_generate_ppt_task_async(
        task_id, user_id, project_id, content_json, template_id, ai_model, db_url
    ))


def generate_ppt_task_with_ai(
    task_id: str,
    user_id: int,
    project_id: int,
    description: str,
    page_count: int,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    import asyncio
    asyncio.run(_generate_ppt_task_with_ai_async(
        task_id, user_id, project_id, description, page_count, template_id, ai_model, db_url
    ))


def generate_ppt_task_with_outline(
    task_id: str,
    user_id: int,
    project_id: int,
    outline: dict,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    import asyncio
    asyncio.run(_generate_ppt_task_with_outline_async(
        task_id, user_id, project_id, outline, template_id, ai_model, db_url
    ))


def generate_ppt_task_with_document(
    task_id: str,
    user_id: int,
    project_id: int,
    text_content: str,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    import asyncio
    asyncio.run(_generate_ppt_task_with_document_async(
        task_id, user_id, project_id, text_content, template_id, ai_model, db_url
    ))


async def _generate_ppt_task_with_ai_async(
    task_id: str,
    user_id: int,
    project_id: int,
    description: str,
    page_count: int,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        try:
            generation_tasks[task_id] = {
                "status": "processing",
                "progress": 5,
                "message": "正在初始化AI服务..."
            }
            
            ai_service = AIServiceFactory.get_service(ai_model)
            
            generation_tasks[task_id]["progress"] = 10
            generation_tasks[task_id]["message"] = "正在生成大纲..."
            
            outline = await ai_service.generate_outline(description, page_count)
            
            generation_tasks[task_id]["progress"] = 25
            generation_tasks[task_id]["message"] = "正在扩展内容..."
            
            content_json = await ai_service.expand_content(outline)
            
            generation_tasks[task_id]["progress"] = 40
            generation_tasks[task_id]["message"] = "正在准备生成PPT..."
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            
            if not project:
                generation_tasks[task_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": "项目不存在"
                }
                return
            
            template = None
            if template_id:
                template = db.execute(
                    select(Template).where(Template.id == template_id)
                ).scalar_one_or_none()
            
            if template and template.template_data:
                content_json["theme"] = template.template_data
            
            project.title = content_json.get("title", "未命名PPT")
            project.content_json = content_json
            db.commit()
            
            generation_tasks[task_id]["progress"] = 45
            generation_tasks[task_id]["message"] = "正在生成PPT幻灯片..."
            
            generator = PPTGenerator()
            generator.generate_from_json(content_json, progress_callback=lambda p, m: update_progress(task_id, p, m))
            
            generation_tasks[task_id]["progress"] = 85
            generation_tasks[task_id]["message"] = "正在保存文件..."
            
            ppt_bytes = generator.save_to_bytes()
            
            generation_tasks[task_id]["progress"] = 90
            generation_tasks[task_id]["message"] = "正在上传文件..."
            
            storage = get_storage_service()
            file_url = await storage.upload_bytes(
                ppt_bytes,
                folder="ppt",
                filename=f"{content_json.get('title', '未命名PPT')}.pptx"
            )
            
            project.file_url = file_url
            project.file_size = len(ppt_bytes)
            project.status = "completed"
            project.page_count = len(content_json.get("pages", []))
            db.commit()
            
            history = GenerationHistory(
                user_id=user_id,
                project_id=project_id,
                input_type="text",
                ai_model=ai_model,
                status="success"
            )
            db.add(history)
            db.commit()
            
            generation_tasks[task_id] = {
                "status": "completed",
                "progress": 100,
                "message": "PPT生成完成",
                "result": {
                    "project_id": project_id,
                    "file_url": file_url
                }
            }
            
        except Exception as e:
            generation_tasks[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": str(e)
            }
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            if project:
                project.status = "failed"
                db.commit()


def update_progress(task_id: str, progress: int, message: str):
    if task_id in generation_tasks:
        generation_tasks[task_id]["progress"] = progress
        generation_tasks[task_id]["message"] = message


async def _generate_ppt_task_async(
    task_id: str,
    user_id: int,
    project_id: int,
    content_json: dict,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        try:
            generation_tasks[task_id] = {
                "status": "processing",
                "progress": 10,
                "message": "正在生成PPT..."
            }
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            
            if not project:
                generation_tasks[task_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": "项目不存在"
                }
                return
            
            template = None
            if template_id:
                template = db.execute(
                    select(Template).where(Template.id == template_id)
                ).scalar_one_or_none()
            
            if template and template.template_data:
                content_json["theme"] = template.template_data
                print(f"[DEBUG] generate_ppt_task: Injected theme data: {template.template_data}")
            
            project.title = content_json.get("title", "未命名PPT")
            project.content_json = content_json
            db.commit()
            
            generation_tasks[task_id]["progress"] = 20
            generation_tasks[task_id]["message"] = "正在生成PPT幻灯片..."
            
            generator = PPTGenerator()
            generator.generate_from_json(content_json, progress_callback=lambda p, m: update_progress(task_id, p, m))
            
            generation_tasks[task_id]["progress"] = 85
            generation_tasks[task_id]["message"] = "正在保存文件..."
            
            ppt_bytes = generator.save_to_bytes()
            
            generation_tasks[task_id]["progress"] = 90
            generation_tasks[task_id]["message"] = "正在上传文件..."
            
            storage = get_storage_service()
            file_url = await storage.upload_bytes(
                ppt_bytes,
                folder="ppt",
                filename=f"{project.title}.pptx"
            )
            
            project.file_url = file_url
            project.file_size = len(ppt_bytes)
            project.status = "completed"
            project.page_count = len(content_json.get("pages", []))
            db.commit()
            
            history = GenerationHistory(
                user_id=user_id,
                project_id=project_id,
                input_type="text",
                ai_model=ai_model,
                status="success"
            )
            db.add(history)
            db.commit()
            
            generation_tasks[task_id] = {
                "status": "completed",
                "progress": 100,
                "message": "PPT生成完成",
                "result": {
                    "project_id": project_id,
                    "file_url": file_url
                }
            }
            
        except Exception as e:
            generation_tasks[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": str(e)
            }
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            if project:
                project.status = "failed"
                db.commit()


async def _generate_ppt_task_with_outline_async(
    task_id: str,
    user_id: int,
    project_id: int,
    outline: dict,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        try:
            generation_tasks[task_id] = {
                "status": "processing",
                "progress": 5,
                "message": "正在初始化AI服务..."
            }
            
            ai_service = AIServiceFactory.get_service(ai_model)
            
            generation_tasks[task_id]["progress"] = 10
            generation_tasks[task_id]["message"] = "正在扩展内容..."
            
            content_json = await ai_service.expand_content(outline)
            
            generation_tasks[task_id]["progress"] = 25
            generation_tasks[task_id]["message"] = "正在准备生成PPT..."
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            
            if not project:
                generation_tasks[task_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": "项目不存在"
                }
                return
            
            template = None
            if template_id:
                template = db.execute(
                    select(Template).where(Template.id == template_id)
                ).scalar_one_or_none()
            
            if template and template.template_data:
                content_json["theme"] = template.template_data
            
            project.title = content_json.get("title", "未命名PPT")
            project.content_json = content_json
            db.commit()
            
            generation_tasks[task_id]["progress"] = 30
            generation_tasks[task_id]["message"] = "正在生成PPT幻灯片..."
            
            generator = PPTGenerator()
            generator.generate_from_json(content_json, progress_callback=lambda p, m: update_progress(task_id, p, m))
            
            generation_tasks[task_id]["progress"] = 85
            generation_tasks[task_id]["message"] = "正在保存文件..."
            
            ppt_bytes = generator.save_to_bytes()
            
            generation_tasks[task_id]["progress"] = 90
            generation_tasks[task_id]["message"] = "正在上传文件..."
            
            storage = get_storage_service()
            file_url = await storage.upload_bytes(
                ppt_bytes,
                folder="ppt",
                filename=f"{content_json.get('title', '未命名PPT')}.pptx"
            )
            
            project.file_url = file_url
            project.file_size = len(ppt_bytes)
            project.status = "completed"
            project.page_count = len(content_json.get("pages", []))
            db.commit()
            
            history = GenerationHistory(
                user_id=user_id,
                project_id=project_id,
                input_type="outline",
                ai_model=ai_model,
                status="success"
            )
            db.add(history)
            db.commit()
            
            generation_tasks[task_id] = {
                "status": "completed",
                "progress": 100,
                "message": "PPT生成完成",
                "result": {
                    "project_id": project_id,
                    "file_url": file_url
                }
            }
            
        except Exception as e:
            generation_tasks[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": str(e)
            }
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            if project:
                project.status = "failed"
                db.commit()


async def _generate_ppt_task_with_document_async(
    task_id: str,
    user_id: int,
    project_id: int,
    text_content: str,
    template_id: Optional[int],
    ai_model: str,
    db_url: str
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        try:
            generation_tasks[task_id] = {
                "status": "processing",
                "progress": 5,
                "message": "正在初始化AI服务..."
            }
            
            ai_service = AIServiceFactory.get_service(ai_model)
            
            generation_tasks[task_id]["progress"] = 10
            generation_tasks[task_id]["message"] = "正在解析文档..."
            
            outline = await ai_service.parse_document(text_content)
            
            generation_tasks[task_id]["progress"] = 25
            generation_tasks[task_id]["message"] = "正在扩展内容..."
            
            content_json = await ai_service.expand_content(outline)
            
            generation_tasks[task_id]["progress"] = 40
            generation_tasks[task_id]["message"] = "正在准备生成PPT..."
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            
            if not project:
                generation_tasks[task_id] = {
                    "status": "failed",
                    "progress": 0,
                    "message": "项目不存在"
                }
                return
            
            template = None
            if template_id:
                template = db.execute(
                    select(Template).where(Template.id == template_id)
                ).scalar_one_or_none()
            
            if template and template.template_data:
                content_json["theme"] = template.template_data
            
            project.title = content_json.get("title", "未命名PPT")
            project.content_json = content_json
            db.commit()
            
            generation_tasks[task_id]["progress"] = 45
            generation_tasks[task_id]["message"] = "正在生成PPT幻灯片..."
            
            generator = PPTGenerator()
            generator.generate_from_json(content_json, progress_callback=lambda p, m: update_progress(task_id, p, m))
            
            generation_tasks[task_id]["progress"] = 85
            generation_tasks[task_id]["message"] = "正在保存文件..."
            
            ppt_bytes = generator.save_to_bytes()
            
            generation_tasks[task_id]["progress"] = 90
            generation_tasks[task_id]["message"] = "正在上传文件..."
            
            storage = get_storage_service()
            file_url = await storage.upload_bytes(
                ppt_bytes,
                folder="ppt",
                filename=f"{content_json.get('title', '未命名PPT')}.pptx"
            )
            
            project.file_url = file_url
            project.file_size = len(ppt_bytes)
            project.status = "completed"
            project.page_count = len(content_json.get("pages", []))
            db.commit()
            
            history = GenerationHistory(
                user_id=user_id,
                project_id=project_id,
                input_type="document",
                ai_model=ai_model,
                status="success"
            )
            db.add(history)
            db.commit()
            
            generation_tasks[task_id] = {
                "status": "completed",
                "progress": 100,
                "message": "PPT生成完成",
                "result": {
                    "project_id": project_id,
                    "file_url": file_url
                }
            }
            
        except Exception as e:
            generation_tasks[task_id] = {
                "status": "failed",
                "progress": 0,
                "message": str(e)
            }
            
            project = db.execute(
                select(PPTProject).where(PPTProject.id == project_id)
            ).scalar_one_or_none()
            if project:
                project.status = "failed"
                db.commit()


@router.post("/generate/text")
async def generate_by_text(
    data: PPTGenerateByText,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    print(f"[DEBUG] generate_by_text called with data: {data}")
    print(f"[DEBUG] template_id from request: {data.template_id}")
    
    if not await check_daily_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"免费用户每日生成次数已达上限（{settings.FREE_USER_DAILY_LIMIT}次）"
        )
    
    if data.ai_model == AIModelEnum.KIMI and not current_user.is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kimi模型仅限会员使用"
        )
    
    project = PPTProject(
        user_id=current_user.id,
        title="正在生成...",
        template_id=data.template_id,
        content_json={},
        status="generating"
    )
    print(f"[DEBUG] Creating project with template_id={data.template_id}")
    db.add(project)
    await db.commit()
    await db.refresh(project)
    print(f"[DEBUG] Project created: id={project.id}, template_id={project.template_id}")
    
    await increment_daily_usage(current_user, db)
    
    task_id = str(uuid.uuid4())
    generation_tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "任务已创建"
    }
    
    background_tasks.add_task(
        generate_ppt_task_with_ai,
        task_id,
        current_user.id,
        project.id,
        data.description,
        data.page_count,
        data.template_id,
        data.ai_model.value,
        settings.DATABASE_URL_SYNC
    )
    
    return {
        "task_id": task_id,
        "project_id": project.id,
        "message": "PPT生成任务已创建"
    }


@router.post("/generate/outline")
async def generate_by_outline(
    data: PPTGenerateByOutline,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    if not await check_daily_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"免费用户每日生成次数已达上限（{settings.FREE_USER_DAILY_LIMIT}次）"
        )
    
    if data.ai_model == AIModelEnum.KIMI and not current_user.is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kimi模型仅限会员使用"
        )
    
    outline = {
        "title": data.title,
        "pages": data.outline
    }
    
    project = PPTProject(
        user_id=current_user.id,
        title=data.title,
        template_id=data.template_id,
        content_json={},
        status="generating"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    await increment_daily_usage(current_user, db)
    
    task_id = str(uuid.uuid4())
    generation_tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "任务已创建"
    }
    
    background_tasks.add_task(
        generate_ppt_task_with_outline,
        task_id,
        current_user.id,
        project.id,
        outline,
        data.template_id,
        data.ai_model.value,
        settings.DATABASE_URL_SYNC
    )
    
    return {
        "task_id": task_id,
        "project_id": project.id,
        "message": "PPT生成任务已创建"
    }


@router.post("/generate/document")
async def generate_by_document(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    file: UploadFile = File(...),
    template_id: Optional[int] = Form(None),
    ai_model: AIModelEnum = Form(AIModelEnum.QWEN)
):
    print(f"[DEBUG] generate_by_document called with template_id: {template_id}, ai_model: {ai_model}")
    
    if not await check_daily_limit(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"免费用户每日生成次数已达上限（{settings.FREE_USER_DAILY_LIMIT}次）"
        )
    
    if ai_model == AIModelEnum.KIMI and not current_user.is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kimi模型仅限会员使用"
        )
    
    content = await file.read()
    
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
        )
    
    text_content = ""
    filename = file.filename.lower()
    
    if filename.endswith('.txt') or filename.endswith('.md'):
        text_content = content.decode('utf-8', errors='ignore')
    elif filename.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            text_content = '\n'.join([p.text for p in doc.paragraphs])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法解析Word文档"
            )
    elif filename.endswith('.pdf'):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    lines = page_text.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        cleaned_line = line.strip()
                        if cleaned_line:
                            cleaned_lines.append(cleaned_line)
                    if cleaned_lines:
                        text_parts.append('\n'.join(cleaned_lines))
            text_content = '\n\n'.join(text_parts)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法解析PDF文档"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件格式"
        )
    
    print(f"Extracted content preview (first 500 chars):\n{text_content[:500]}")
    
    project = PPTProject(
        user_id=current_user.id,
        title="正在生成...",
        template_id=template_id,
        content_json={},
        status="generating"
    )
    print(f"[DEBUG] Creating document project with template_id={template_id}")
    db.add(project)
    await db.commit()
    await db.refresh(project)
    print(f"[DEBUG] Document project created: id={project.id}, template_id={project.template_id}")
    
    await increment_daily_usage(current_user, db)
    
    task_id = str(uuid.uuid4())
    generation_tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "任务已创建"
    }
    
    background_tasks.add_task(
        generate_ppt_task_with_document,
        task_id,
        current_user.id,
        project.id,
        text_content,
        template_id,
        ai_model.value,
        settings.DATABASE_URL_SYNC
    )
    
    return {
        "task_id": task_id,
        "project_id": project.id,
        "message": "PPT生成任务已创建"
    }


import io


@router.get("/generate/status/{task_id}", response_model=GenerationStatusResponse)
async def get_generation_status(task_id: str):
    if task_id not in generation_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    task = generation_tasks[task_id]
    return GenerationStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        result=task.get("result")
    )


@router.get("/projects", response_model=PaginatedResponse)
async def get_projects(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    query = select(PPTProject).where(
        PPTProject.user_id == current_user.id,
        PPTProject.is_deleted == False
    ).order_by(PPTProject.updated_at.desc())
    
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return PaginatedResponse(
        items=[PPTProjectResponse.model_validate(p) for p in projects],
        total=total or 0,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0
    )


@router.get("/projects/{project_id}", response_model=PPTProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(PPTProject).where(
            PPTProject.id == project_id,
            PPTProject.user_id == current_user.id,
            PPTProject.is_deleted == False
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return PPTProjectResponse.model_validate(project)


@router.put("/projects/{project_id}", response_model=PPTProjectResponse)
async def update_project(
    project_id: int,
    update_data: PPTProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(PPTProject).where(
            PPTProject.id == project_id,
            PPTProject.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if update_data.title is not None:
        project.title = update_data.title
    if update_data.description is not None:
        project.description = update_data.description
    if update_data.content_json is not None:
        project.content_json = update_data.content_json
    if update_data.status is not None:
        project.status = update_data.status.value
    
    await db.commit()
    await db.refresh(project)
    
    return PPTProjectResponse.model_validate(project)


@router.delete("/projects/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(PPTProject).where(
            PPTProject.id == project_id,
            PPTProject.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    project.is_deleted = True
    await db.commit()
    
    return MessageResponse(message="项目已删除")


@router.get("/projects/{project_id}/export")
async def export_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(PPTProject).where(
            PPTProject.id == project_id,
            PPTProject.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        # 始终重新生成，确保获取最新内容
        generator = PPTGenerator()
        
        # 注入样式配置
        content_json = project.content_json or {}
        
        # 尝试获取模板信息并注入样式（如果 content_json 中没有）
        if project.template_id and "theme" not in content_json:
            template_result = await db.execute(
                select(Template).where(Template.id == project.template_id)
            )
            template = template_result.scalar_one_or_none()
            if template and template.template_data:
                 content_json["theme"] = template.template_data
        
        generator.generate_from_json(content_json, generate_images=False) # 导出时不需要重新生成图片，使用已有的
        ppt_bytes = generator.save_to_bytes()
        
        # 更新文件存储（可选，如果需要持久化最新版本）
        # storage = get_storage_service()
        # file_url = await storage.upload_bytes(...)
            
    except Exception as e:
        print(f"Export error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPT生成失败: {str(e)}"
        )
    
    filename = f"{project.title}.pptx"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        io.BytesIO(ppt_bytes),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
