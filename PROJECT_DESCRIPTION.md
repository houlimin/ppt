# AI PPT 生成平台 - 项目描述

## 项目概述

AI PPT 生成平台是一个基于人工智能的演示文稿自动生成系统，用户可以通过简单的文字描述、大纲或文档上传，快速生成专业美观的 PPT 演示文稿。

## 技术架构

### 后端技术栈
- **框架**: FastAPI (Python 异步框架)
- **数据库**: SQLite (开发环境) / PostgreSQL (生产环境)
- **ORM**: SQLAlchemy (异步模式)
- **认证**: JWT (JSON Web Token)
- **AI 服务**: 
  - 通义千问 (阿里云 DashScope API)
  - Kimi (Moonshot API)
- **PPT 生成**: python-pptx
- **存储**: 本地存储 / 阿里云 OSS

### 前端技术栈
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

## 项目结构

```
ppt/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证相关 API
│   │   │   ├── ppt.py         # PPT 生成 API
│   │   │   ├── template.py    # 模板管理 API
│   │   │   ├── user.py        # 用户管理 API
│   │   │   └── order.py       # 订单支付 API
│   │   ├── core/              # 核心模块
│   │   │   ├── auth.py        # JWT 认证
│   │   │   └── security.py    # 安全工具
│   │   ├── models/            # 数据库模型
│   │   │   └── models.py      # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   │   └── schemas.py     # 请求/响应模型
│   │   ├── services/          # 业务服务
│   │   │   ├── ai_service.py  # AI 服务 (通义千问/Kimi)
│   │   │   ├── ppt_service.py # PPT 生成服务
│   │   │   ├── storage_service.py # 存储服务
│   │   │   └── template_service.py # 模板服务
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── uploads/               # 上传文件存储
│   ├── .env                   # 环境配置
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/               # API 调用
│   │   │   ├── index.js       # Axios 配置
│   │   │   ├── auth.js        # 认证 API
│   │   │   └── ppt.js         # PPT API
│   │   ├── components/        # 公共组件
│   │   ├── layouts/           # 布局组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue      # 登录页
│   │   │   ├── Register.vue   # 注册页
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── Create.vue     # 创建 PPT
│   │   │   ├── Editor.vue     # PPT 编辑器
│   │   │   ├── Projects.vue   # 项目列表
│   │   │   ├── Templates.vue  # 模板中心
│   │   │   └── Profile.vue    # 个人中心
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── package.json           # npm 配置
│   └── vite.config.js         # Vite 配置
│
└── PROJECT_DESCRIPTION.md      # 项目描述文档
```

## 核心功能模块

### 1. 用户认证系统
- 用户注册/登录
- JWT Token 认证
- 用户信息管理
- 会员等级管理

### 2. PPT 生成系统
- **文字描述生成**: 输入主题描述，AI 自动生成完整 PPT
- **大纲生成**: 输入大纲结构，AI 扩展内容
- **文档上传**: 上传 Word/PDF/TXT 文档，AI 提取内容生成 PPT

### 3. AI 服务集成
- **通义千问**: 阿里云 DashScope API，默认模型
- **Kimi**: Moonshot API，会员专属

### 4. 模板系统
- 多种预设主题模板
- 自定义颜色、字体配置
- 模板收藏功能

### 5. 在线编辑器
- 幻灯片预览
- 内容编辑
- 布局切换
- 实时保存

### 6. 导出功能
- PPTX 格式导出
- 文件下载

### 7. 会员系统
- 免费用户: 每日 3 次生成限制
- 会员用户: 无限制 + Kimi 模型

## 数据库模型

### User (用户)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名 |
| email | String | 邮箱 |
| password_hash | String | 密码哈希 |
| membership_type | String | 会员类型 |
| membership_expire_at | DateTime | 会员过期时间 |

### PPTProject (PPT 项目)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户 ID |
| title | String | 标题 |
| content_json | JSON | 内容数据 |
| file_url | String | 文件 URL |
| status | String | 状态 |

### Template (模板)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 模板名称 |
| template_data | JSON | 模板配置 |
| is_premium | Boolean | 是否付费 |

### Order (订单)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户 ID |
| order_no | String | 订单号 |
| amount | Float | 金额 |
| status | String | 状态 |

## API 接口

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户

### PPT 接口
- `POST /api/v1/ppt/generate/text` - 文字描述生成
- `POST /api/v1/ppt/generate/outline` - 大纲生成
- `POST /api/v1/ppt/generate/document` - 文档上传生成
- `GET /api/v1/ppt/generate/status/{task_id}` - 查询生成状态
- `GET /api/v1/ppt/projects` - 项目列表
- `GET /api/v1/ppt/projects/{id}` - 项目详情
- `PUT /api/v1/ppt/projects/{id}` - 更新项目
- `DELETE /api/v1/ppt/projects/{id}` - 删除项目
- `GET /api/v1/ppt/projects/{id}/export` - 导出 PPT

### 模板接口
- `GET /api/v1/templates` - 模板列表
- `GET /api/v1/templates/{id}` - 模板详情

### 用户接口
- `GET /api/v1/users/me` - 获取用户信息
- `PUT /api/v1/users/me` - 更新用户信息

## 环境配置

### 后端环境变量 (.env)
```env
DEBUG=true
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./ai_ppt_v2.db
DASHSCOPE_API_KEY=your-dashscope-api-key
MOONSHOT_API_KEY=your-moonshot-api-key
```

### 前端配置
- API 代理: `/api` -> `http://localhost:8000/api/v1`

## 启动方式

### 后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 访问地址
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 待完善功能

1. **支付集成**: 支付宝/微信支付
2. **更多 AI 模型**: 支持 GPT、Claude 等
3. **协作功能**: 多人协作编辑
4. **历史版本**: 版本管理与回滚
5. **分享功能**: 在线分享与嵌入
6. **更多模板**: 行业模板库
7. **图表生成**: 数据可视化图表
8. **图片生成**: AI 图片生成集成
