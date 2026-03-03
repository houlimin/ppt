from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Template


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_templates(
        self,
        category: Optional[str] = None,
        is_premium: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Template], int]:
        query = select(Template).where(Template.is_active == True)
        
        if category:
            query = query.where(Template.category == category)
        
        if is_premium is not None:
            query = query.where(Template.is_premium == is_premium)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        query = query.order_by(Template.download_count.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return list(templates), total or 0
    
    async def get_template_by_id(self, template_id: int) -> Optional[Template]:
        result = await self.db.execute(
            select(Template).where(Template.id == template_id, Template.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        return [
            {"value": "business", "label": "商务类"},
            {"value": "education", "label": "教育类"},
            {"value": "creative", "label": "创意类"},
            {"value": "industry", "label": "行业类"}
        ]
    
    async def increment_download_count(self, template_id: int):
        template = await self.get_template_by_id(template_id)
        if template:
            template.download_count += 1
            await self.db.commit()


DEFAULT_TEMPLATES = [
    # 商务类模板 (5个)
    {
        "name": "简约商务蓝",
        "category": "business",
        "description": "简洁专业的商务风格，适合企业汇报、项目提案",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "business_blue",
            "primary_color": [0, 112, 192],
            "secondary_color": [68, 84, 106],
            "background_color": [240, 248, 255],
            "accent_color": [255, 192, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "科技深蓝",
        "category": "business",
        "description": "现代科技感设计，适合科技公司、产品发布",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "tech_dark_blue",
            "primary_color": [0, 150, 255],
            "secondary_color": [100, 180, 220],
            "background_color": [20, 30, 50],
            "accent_color": [0, 255, 200],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "商务深色",
        "category": "business",
        "description": "沉稳大气的深色主题，适合高端商务场合",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "business_dark",
            "primary_color": [220, 220, 220],
            "secondary_color": [180, 180, 180],
            "background_color": [35, 35, 40],
            "accent_color": [100, 200, 150],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "极简白",
        "category": "business",
        "description": "极简主义设计，干净清爽，适合各类商务场景",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "minimal_white",
            "primary_color": [0, 0, 0],
            "secondary_color": [128, 128, 128],
            "background_color": [255, 255, 255],
            "accent_color": [200, 200, 200],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "金融专业",
        "category": "business",
        "description": "专业金融风格，适合银行、投资、财务报告",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "finance_pro",
            "primary_color": [0, 64, 128],
            "secondary_color": [64, 128, 128],
            "background_color": [235, 242, 250],
            "accent_color": [218, 165, 32],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    
    # 教育类模板 (5个)
    {
        "name": "教育清新绿",
        "category": "education",
        "description": "清新自然的教育风格，适合学校、培训机构",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "education_green",
            "primary_color": [34, 139, 34],
            "secondary_color": [60, 179, 113],
            "background_color": [220, 245, 220],
            "accent_color": [255, 200, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "学术严谨",
        "category": "education",
        "description": "严谨学术风格，适合论文答辩、学术报告",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "academic_serious",
            "primary_color": [70, 70, 70],
            "secondary_color": [100, 100, 100],
            "background_color": [250, 248, 240],
            "accent_color": [139, 69, 19],
            "title_font": "宋体",
            "body_font": "宋体"
        }
    },
    {
        "name": "幼儿园活泼",
        "category": "education",
        "description": "活泼可爱的风格，适合幼儿教育、亲子活动",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "kindergarten",
            "primary_color": [255, 105, 180],
            "secondary_color": [255, 182, 193],
            "background_color": [255, 240, 245],
            "accent_color": [255, 200, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "大学讲座",
        "category": "education",
        "description": "专业大学讲座风格，适合公开课、学术讲座",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "university_lecture",
            "primary_color": [0, 51, 102],
            "secondary_color": [102, 102, 153],
            "background_color": [245, 248, 252],
            "accent_color": [192, 192, 192],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "在线课程",
        "category": "education",
        "description": "现代在线教育风格，适合网课、远程教学",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "online_course",
            "primary_color": [70, 130, 180],
            "secondary_color": [135, 206, 235],
            "background_color": [235, 245, 255],
            "accent_color": [255, 140, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    
    # 创意类模板 (5个)
    {
        "name": "创意活力橙",
        "category": "creative",
        "description": "充满活力的橙色主题，适合创意提案、营销方案",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "creative_orange",
            "primary_color": [255, 102, 0],
            "secondary_color": [255, 153, 51],
            "background_color": [255, 245, 235],
            "accent_color": [0, 102, 204],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "艺术紫韵",
        "category": "creative",
        "description": "优雅紫色主题，适合艺术设计、品牌展示",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "artistic_purple",
            "primary_color": [128, 0, 128],
            "secondary_color": [186, 85, 211],
            "background_color": [245, 240, 255],
            "accent_color": [255, 215, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "时尚粉红",
        "category": "creative",
        "description": "时尚粉色主题，适合时尚、美妆、女性产品",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "fashion_pink",
            "primary_color": [255, 20, 147],
            "secondary_color": [255, 105, 180],
            "background_color": [255, 235, 245],
            "accent_color": [255, 182, 193],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "自然绿意",
        "category": "creative",
        "description": "自然清新风格，适合环保、健康、生活方式",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "nature_green",
            "primary_color": [60, 120, 60],
            "secondary_color": [144, 180, 75],
            "background_color": [235, 250, 235],
            "accent_color": [255, 200, 87],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "复古怀旧",
        "category": "creative",
        "description": "复古怀旧风格，适合历史回顾、品牌故事",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "vintage",
            "primary_color": [139, 90, 43],
            "secondary_color": [160, 120, 80],
            "background_color": [250, 240, 225],
            "accent_color": [205, 133, 63],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    
    # 行业类模板 (5个)
    {
        "name": "医疗健康",
        "category": "industry",
        "description": "专业医疗风格，适合医院、诊所、健康机构",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "medical_health",
            "primary_color": [0, 128, 128],
            "secondary_color": [72, 209, 204],
            "background_color": [230, 250, 250],
            "accent_color": [255, 99, 71],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "科技互联网",
        "category": "industry",
        "description": "互联网科技风格，适合科技公司、创业路演",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "tech_internet",
            "primary_color": [100, 180, 255],
            "secondary_color": [150, 200, 255],
            "background_color": [25, 35, 55],
            "accent_color": [0, 255, 200],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "建筑工程",
        "category": "industry",
        "description": "建筑工程风格，适合建筑公司、工程项目",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "construction",
            "primary_color": [139, 69, 19],
            "secondary_color": [160, 82, 45],
            "background_color": [250, 245, 235],
            "accent_color": [255, 140, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "餐饮美食",
        "category": "industry",
        "description": "美食餐饮风格，适合餐厅、食品品牌",
        "is_premium": False,
        "is_system": True,
        "template_data": {
            "theme": "food_restaurant",
            "primary_color": [178, 34, 34],
            "secondary_color": [205, 92, 92],
            "background_color": [255, 248, 235],
            "accent_color": [255, 200, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    },
    {
        "name": "旅游度假",
        "category": "industry",
        "description": "旅游度假风格，适合旅行社、酒店、景点",
        "is_premium": True,
        "is_system": True,
        "template_data": {
            "theme": "travel_vacation",
            "primary_color": [0, 139, 139],
            "secondary_color": [32, 178, 170],
            "background_color": [230, 250, 250],
            "accent_color": [255, 165, 0],
            "title_font": "微软雅黑",
            "body_font": "微软雅黑"
        }
    }
]


async def init_default_templates(db: AsyncSession):
    for template_data in DEFAULT_TEMPLATES:
        result = await db.execute(
            select(Template).where(Template.name == template_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.template_data = template_data["template_data"]
            existing.description = template_data["description"]
            existing.category = template_data["category"]
            existing.is_premium = template_data["is_premium"]
        else:
            template = Template(**template_data)
            db.add(template)
    await db.commit()


class UserTemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user_template(
        self,
        user_id: int,
        name: str,
        category: str,
        description: str,
        template_data: dict,
        thumbnail_url: str = None
    ) -> Template:
        template = Template(
            name=name,
            category=category,
            description=description,
            template_data=template_data,
            thumbnail_url=thumbnail_url,
            is_system=False,
            is_premium=False,
            creator_id=user_id,
            is_active=True
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def get_user_templates(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Template], int]:
        query = select(Template).where(
            Template.creator_id == user_id,
            Template.is_active == True
        )
        
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)
        
        query = query.order_by(Template.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        templates = result.scalars().all()
        
        return list(templates), total or 0
    
    async def update_user_template(
        self,
        template_id: int,
        user_id: int,
        **kwargs
    ) -> Optional[Template]:
        result = await self.db.execute(
            select(Template).where(
                Template.id == template_id,
                Template.creator_id == user_id,
                Template.is_active == True
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            return None
        
        for key, value in kwargs.items():
            if hasattr(template, key) and value is not None:
                setattr(template, key, value)
        
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def delete_user_template(
        self,
        template_id: int,
        user_id: int
    ) -> bool:
        result = await self.db.execute(
            select(Template).where(
                Template.id == template_id,
                Template.creator_id == user_id
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            return False
        
        template.is_active = False
        await self.db.commit()
        return True
