# RAG 知识库 AI 应用 MVP

## 1. MVP基本技术栈

实现最基本的知识库构建与更新模块+AI对话框模块

### 前端UI

**Vue.js + Vite + Tauri (Web-to-Desktop 封装器)**

- 用户界面，负责文件导入，与AI助手对话等交互。Tauri封装后可发布为轻量本地桌面引用。
- 前后端监听方式：（协议 HTTP Restful API）FastAPI 默认监听本地端口，Vue前端通过 axios 发起 HTTP 请求到 FastAPI 提供的接口。
- 使用了现有前端 UI 解决方案：[MateChat](https://matechat.gitcode.com/)

### 后端

**FastAPI**

- 主业务入口，负责接收前端请求，调度各个模块（批量文件解析，embedding，检索，LLM交互等），并返回处理结果。
- 这么设计前后端搭配是为提供了后期将后端迁移到服务器的可能：本地-服务器混合服务，Tauri客户端在本地运行，而 FastAPI 后端部署在服务器中。

### 文件解析

先实现解析最基础的.txt文件，后面再加入各类 python 库解析模块

### 内容结构化与分段

Python 静态函数实现

### 传统数据库

**SQLite**

- 主要设计目的用于存储表结构数据，主要有：
  - 文档：用户导入的每一个文件，记录了文件的原始信息，路径，类型，解析状态等。
  - 知识条目：记录文件的原始信息，路径，类型，解析状态等，每一个条目都拥有一个与 embedding 对应向量数据绑定 id
- 知识条目的 embedding 向量数据不储存于此
- 增加未来开发的可拓展性，可以通过添加新的表结构，结合扩展开发实现历史留存，多用户权限管理等新特性。

### Embedding 模块

**Sentence-transformers Huggingface**

- 将文本内容编码为可被 LLM 理解的高维数值表示，便于后续的语义相似度检索。先试用较为轻量的向量模型进行试验。
- 模型链接：[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

### 向量库数据库设计

**Chroma/FAISS**

- 专门储存于管理知识条目的 embedding 向量数据，并支持快速相似度检索。
- 每一个embedding 对应向量数据都拥有一个与 SQLite 数据库中的表数据绑定 id

### RAG（Retrieval-augmented Generation）检索增强生成流程

**LangChain/Haystack**

- 让大预言模型回答时有理有据，使其能够引用本地知识库内容，使答案更准确，可溯源

### LLM API

设置可配置 API key，支持多种 LLM 服务

### 技术栈流程图

> TODO: 添加技术栈流程图

## 2. 数据库表结构设计

### 2.1 ApplicationLog 表 (应用日志)

| 字段名       | 类型        | 说明           |
| ----------- | ----------- | -------------- |
| id          | int         | 主键，自增     |
| session_id  | str         | 会话唯一标识   |
| user_query  | str         | 用户查询内容   |
| gpt_response| str         | AI回复内容     |
| model       | str         | 使用的模型名称 |
| created_at  | datetime    | 创建时间       |

### 2.2 DocumentStore 表 (文档存储)

| 字段名            | 类型      | 说明             |
| ---------------- | --------- | ---------------- |
| id               | int       | 主键，自增       |
| filename         | str       | 文件名           |
| upload_timestamp | datetime  | 上传时间戳       |

### 2.3 向量数据库 (Chroma)

向量数据通过 Chroma 向量数据库管理，不存储在 SQLite 中：

- **文档切片向量化存储**：每个上传文档被切分成多个片段，每个片段生成对应的向量
- **元数据关联**：向量数据包含对应的文档ID，与 DocumentStore 表关联
- **语义检索**：支持基于向量相似度的语义检索和RAG问答

## 3. MVP功能结构图/模块划分

### 3.1 知识库构建与更新模块

首先实现 MVP 部分：

> TODO: 添加功能结构图

### 3.2 用户与助手交互（AI 对话框）

首先实现 MVP 部分：

> TODO: 添加交互流程图

## 4. 项目结构

```
InfoPop/
├── frontend/           # Vue.js 前端
├── backend/           # FastAPI 后端
│   ├── app/          # 应用主要代码
│   └── prompts/      # AI 提示词配置
└── README.md         # 项目说明
```

## 5. 安装与运行

### 5.1 环境要求

- Node.js: v22.17.1
- Python: 3.13.5
- Rust: 1.89.0 (Tauri 依赖)

### 5.2 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 5.3 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 6. MVP FastAPI 后端接口数据结构设计

### 6.1 `/chat` - 对话与问答

**请求格式：**
```json
{
  "message": "string",              // 用户输入的问题
  "conversation_id": "string",      // 可选，会话唯一标识
  "model_name": "string"            // 可选，默认为 gpt-3.5-turbo
}
```

**响应格式：**
```json
{
  "message": "string",              // LLM生成的答案
  "conversation_id": "string",      // 会话唯一标识
  "model_used": "string",           // 使用的模型名称
  "timestamp": "datetime"           // 响应时间戳
}
```

### 6.2 `/upload-documents` - 上传文档并索引

**请求格式：** 
- 使用 multipart/form-data 上传文件
- 支持的文件类型：.txt, .pdf, .docx, .xlsx

**响应格式：**
```json
{
  "message": "string",              // 上传状态消息
  "file_id": "integer",             // 文件ID（数据库生成）
  "filename": "string",             // 文件名
  "size": "integer"                 // 文件大小（字节）
}
```

### 6.3 `/documents` - 获取已上传文档列表

**响应格式：**
```json
[
  {
    "id": "integer",                // 文档ID
    "filename": "string",           // 文件名
    "upload_timestamp": "datetime"  // 上传时间
  }
]
```

### 6.4 `/documents/{file_id}` - 删除指定文档

**请求方法：** DELETE

**响应格式：**
```json
{
  "message": "string"               // 删除结果消息
}
```

### 6.5 `/conversation/{conversation_id}` - 获取会话历史

**响应格式：**
```json
[
  {
    "content": "string",            // 消息内容
    "from_user": "boolean",         // 是否来自用户
    "timestamp": "datetime"         // 消息时间戳
  }
]
```

### 6.6 `/conversation/{conversation_id}` - 清空会话历史

**请求方法：** DELETE

**响应格式：**
```json
{
  "message": "Conversation cleared successfully"
}
```

### 6.7 `/models` - 获取可用模型列表

**响应格式：**
```json
[
  {
    "model_name": "string",         // 模型名称
    "description": "string",        // 模型描述
    "provider": "string"            // 提供商
  }
]
```

### 6.8 `/health` - 健康检查

**响应格式：**
```json
{
  "status": "healthy",
  "timestamp": "datetime"
}
```

## 7. 依赖配置表

### 7.1 开发环境版本

| 技术栈 | 版本 | 说明 |
|--------|------|------|
| Node.js | v22.17.1 | 前端运行环境 |
| npm | 11.4.2 | 包管理器 |
| Python | 3.13.5 | 后端开发语言 |
| FastAPI | 0.116.1 | Web框架 |
| Rustc | 1.89.0 | Tauri 依赖 |
| MSVC Rust 工具链 | stable-x86_64-pc-windows-msvc | Tauri 构建工具 |

### 7.2 前端依赖

- **axios** (v1.11.0) - 前后端通讯

### 7.3 后端依赖

通过 pip 安装以下包：

- **fastapi** - Web框架
- **pydantic** - 数据验证
- **langchain** - RAG框架
- **langchain-openai** - OpenAI集成
- **openai** - OpenAI API客户端
- **python-dotenv** - 环境变量管理
- **sqlmodel** - ORM框架
- **sqlite3** - 数据库（Python内置）
- **uvicorn** - ASGI服务器

### 7.4 服务启动命令

**后端FastAPI服务：**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

**前端开发服务：**
```bash
npm run dev
```

### 7.5 Prompt 配置系统

项目支持动态 AI 提示词配置：

- 配置文件位置：`backend/prompts/`
- 支持格式：JSON
- 默认配置：`AI_Agent_Prompt.json`
- 备用配置：`Simple_Assistant.json`

**使用方法：**
```python
from prompt_loader import get_system_prompt

# 使用默认AI代理提示词
prompt = get_system_prompt("AI_Agent_Prompt")

# 使用简单助手提示词  
prompt = get_system_prompt("Simple_Assistant")
```


