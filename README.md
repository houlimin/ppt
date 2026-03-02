# AI PPT 生成平台

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.3+-brightgreen.svg)](https://vuejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于大语言模型的智能 PPT 生成平台，支持多种输入方式，一键生成专业演示文稿。

## 项目简介

**一句话描述**：通过 AI 技术自动生成专业 PPT，支持文字描述、大纲、文档上传等多种输入方式。

**核心特性**：
- **多种生成方式**：支持文字描述、大纲结构、文档上传（Word/PDF/Markdown）三种生成方式
- **AI 智能配图**：根据幻灯片内容自动生成相关配图，提升视觉效果
- **多模型支持**：集成通义千问（Qwen）、Kimi（Moonshot）等主流大模型
- **在线编辑器**：实时预览、内容编辑、布局切换
- **会员体系**：免费用户每日限额，会员享受更多权益

## 快速开始

### 前提条件

- Python 3.10+
- Node.js 18+
- SQLite（开发环境）/ PostgreSQL（生产环境）
- Redis（可选，用于缓存）

### 安装与运行

#### 方式一：本地开发模式

```bash
# 1. 克隆项目
git clone https://github.com/your-username/ai-ppt-generator.git
cd ai-ppt-generator

# 2. 配置后端环境变量
cd backend
cp .env.example .env
# 编辑 .env 文件，配置 API 密钥

# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. 安装前端依赖（新终端）
cd ../frontend
npm install

# 6. 启动前端服务
npm run dev
```

#### 方式二：Docker Compose（推荐生产环境）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/ai-ppt-generator.git
cd ai-ppt-generator

# 2. 配置环境变量
export DASHSCOPE_API_KEY=your-dashscope-api-key
export MOONSHOT_API_KEY=your-moonshot-api-key

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 访问地址

- 前端应用：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## 使用方法

### 1. 用户注册与登录

首次使用需要注册账号，支持用户名/邮箱登录。

### 2. 创建 PPT

#### 文字描述生成
输入主题描述，如："制作一份关于人工智能发展史的演示文稿"，AI 将自动生成完整 PPT。

#### 大纲结构生成
输入大纲结构，AI 将扩展内容：
```
1. 项目背景
2. 技术方案
3. 实施计划
4. 预期成果
```

#### 文档上传生成
上传 Word、PDF 或 Markdown 文档，AI 将解析内容并生成 PPT。

### 3. 编辑与导出

- 在线编辑器支持实时预览
- 支持修改标题、内容
- 一键导出 PPTX 格式

## 项目结构

```
ppt/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── ppt.py         # PPT 生成
│   │   │   ├── template.py    # 模板管理
│   │   │   ├── user.py        # 用户管理
│   │   │   └── payment.py     # 支付功能
│   │   ├── core/              # 核心模块
│   │   │   └── auth.py        # JWT 认证
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务服务
│   │   │   ├── ai_service.py  # AI 服务
│   │   │   ├── ppt_service.py # PPT 生成
│   │   │   ├── image_service.py # 图片生成
│   │   │   └── storage_service.py # 存储服务
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试文件
│   ├── uploads/               # 上传文件
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── api/               # API 调用
│   │   ├── layouts/           # 布局组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── styles/            # 样式文件
│   │   ├── views/             # 页面组件
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── Create.vue     # 创建页
│   │   │   ├── Editor.vue     # 编辑器
│   │   │   ├── Projects.vue   # 项目列表
│   │   │   ├── Templates.vue  # 模板中心
│   │   │   ├── Profile.vue    # 个人中心
│   │   │   └── Pricing.vue    # 定价页
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── tests/                 # 测试文件
│   └── package.json           # npm 配置
│
├── docker-compose.yml         # Docker 编排
└── README.md                  # 项目说明
```

## 技术栈

### 后端
| 技术 | 版本 | 说明 |
|------|------|------|
| FastAPI | 0.104+ | 异步 Web 框架 |
| SQLAlchemy | 2.0+ | ORM 框架 |
| python-pptx | 0.6.21+ | PPT 生成库 |
| httpx | 0.25+ | HTTP 客户端 |
| PyPDF2 | 3.0+ | PDF 解析 |
| python-docx | 1.1+ | Word 文档解析 |
| DashScope | 1.14+ | 阿里云 AI SDK |

### 前端
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.3+ | 前端框架 |
| Vue Router | 4.2+ | 路由管理 |
| Pinia | 2.1+ | 状态管理 |
| Element Plus | 2.4+ | UI 组件库 |
| Axios | 1.6+ | HTTP 客户端 |
| Vite | 5.0+ | 构建工具 |

### AI 模型
- **通义千问（Qwen）**：阿里云 DashScope API，默认模型
- **Kimi（Moonshot）**：Moonshot AI API，会员专属

## 环境变量配置

### 后端环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEBUG | 调试模式 | false |
| SECRET_KEY | JWT 密钥 | - |
| DATABASE_URL | 异步数据库 URL | sqlite+aiosqlite:///./ai_ppt.db |
| REDIS_URL | Redis 连接 URL | redis://localhost:6379/0 |
| DASHSCOPE_API_KEY | 通义千问 API 密钥 | - |
| MOONSHOT_API_KEY | Kimi API 密钥 | - |
| OSS_ACCESS_KEY_ID | 阿里云 OSS Key | - |
| OSS_ACCESS_KEY_SECRET | 阿里云 OSS Secret | - |

### 配置示例

```env
# backend/.env
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

DATABASE_URL=sqlite+aiosqlite:///./ai_ppt.db
REDIS_URL=redis://localhost:6379/0

DASHSCOPE_API_KEY=sk-your-dashscope-api-key
MOONSHOT_API_KEY=sk-your-moonshot-api-key

CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## API 文档

启动后端服务后，访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/ppt/generate/text | 文字描述生成 |
| POST | /api/v1/ppt/generate/outline | 大纲生成 |
| POST | /api/v1/ppt/generate/document | 文档上传生成 |
| GET | /api/v1/ppt/projects | 项目列表 |
| GET | /api/v1/ppt/projects/{id}/export | 导出 PPT |
| GET | /api/v1/templates | 模板列表 |

## 贡献指南

我们欢迎所有形式的贡献！

### 报告问题

如果您发现了 Bug 或有功能建议，请：
1. 在 Issues 中搜索是否已有相关问题
2. 如果没有，创建新的 Issue，详细描述问题或建议

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- Python 代码遵循 PEP 8 规范
- JavaScript/Vue 代码使用 ESLint 检查
- 提交信息使用约定式提交格式

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [python-pptx](https://python-pptx.readthedocs.io/) - Python PPT 生成库
- [通义千问](https://dashscope.aliyun.com/) - 阿里云大语言模型
