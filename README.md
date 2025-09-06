# 个人知识助手

一个集成了AI对话、云笔记和团队协作功能的个人知识管理平台。

## 功能特性

- 🤖 **智能AI对话** - 基于深度学习的问答系统
- 📝 **云笔记管理** - 支持Markdown的笔记系统
- 👥 **团队协作** - 组织管理和知识共享
- 🔐 **安全认证** - JWT身份验证和权限控制
- 🗂️ **文件存储** - MinIO对象存储支持
- 💬 **实时通信** - WebSocket实时消息推送

## 技术栈

### 后端

- **FastAPI** - 高性能Python Web框架
- **MySQL** - 关系型数据库
- **MinIO** - 对象存储服务
- **ChromaDB** - 向量数据库（用于AI语义搜索）
- **JWT** - 身份认证
- **SQLAlchemy** - ORM框架

### 前端

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 前端构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

## 项目结构

``` bash
personal-knowledge-assistant/
├── back_end/                 # 后端代码
│   ├── app/                 # 应用核心代码
│   │   ├── ask_question/    # AI问答模块
│   │   ├── Conversation/    # 对话管理
│   │   ├── database/        # 数据库模型
│   │   ├── notes/           # 笔记服务
│   │   ├── organization/    # 组织管理
│   │   └── User/            # 用户管理
│   ├── chroma_db/           # 向量数据库数据
│   ├── .env                 # 环境变量（从.example复制）
│   ├── .env.example         # 环境变量模板
│   ├── requirements.txt     # Python依赖
│   └── main.py             # 应用入口
├── front_end/               # 前端代码
│   ├── src/
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面视图
│   │   ├── stores/          # 状态管理
│   │   ├── services/        # API服务
│   │   └── types/           # TypeScript类型定义
│   ├── package.json         # 前端依赖
│   └── vite.config.ts       # Vite配置
└── knowledge_assistant.sql  # 数据库初始化脚本
```

## 安装和运行

### 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- MinIO (对象存储)

### 后端设置

#### 首次运行前准备

1. **创建虚拟环境**：

   ```bash
   cd back_end
   python -m venv venv
   ```

2. **激活虚拟环境**：
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **安装依赖**：

   ```bash
   pip install -r requirements.txt
   ```

4. **设置MinIO**：
   - 下载MinIO并解压
   - 在minio.exe所在目录创建`data`文件夹
   - 启动MinIO：`minio.exe server data`
   - 默认用户名/密码：minioadmin/minioadmin

5. **数据库初始化**：
   - 创建MySQL数据库：`knowledge_assistant`
   - 导入初始化SQL：
  
     ```sql
     mysql -u root -p knowledge_assistant < knowledge_assistant.sql
     ```

6. **环境配置**：

   ```bash
   cp .env.example .env
   # 编辑.env文件，根据实际情况修改配置
   ```

7. **创建管理员用户**：

   ```python
   # 生成密码哈希
   import hashlib
   password = "your_admin_password"
   hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
   print("Hashed password:", hashed_password)
   ```

   ```sql
   -- 在MySQL中执行
   INSERT INTO users (username, email, hashed_password, created_at, updated_at, is_admin)
   VALUES ('admin', 'admin@example.com', '生成的哈希值', NOW(), NOW(), 1);
   ```

#### 每次运行

1. **启动MinIO**：

   ```bash
   # 在Min目录下
   minio.exe server data
   ```

2. **启动后端服务**：

   ```bash
   cd back_end
   venv\Scripts\activate
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 前端设置

#### 首次运行前

1. **安装Node.js**：从官网下载安装

2. **安装依赖**：

   ```bash
   cd front_end
   npm install
   ```

#### 运行时

```bash
cd front_end
npm run dev
```

前端服务将在 <http://localhost:3000> 启动

## 访问应用

- **前端地址**: <http://localhost:3000>
- **后端API**: <http://localhost:8000>
- **API文档**: <http://localhost:8000/docs>
- **MinIO控制台**: <http://localhost:9001> (用户名/密码: minioadmin)

## 默认管理员账号

- 用户名: admin
- 邮箱: <admin@example.com>
- 密码: 您在设置时指定的密码

## 环境变量配置

在`back_end/.env`中配置以下重要参数：

```env
# 数据库连接
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/knowledge_assistant

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# JWT密钥（生产环境务必修改）
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI服务配置
ZHIPUAI_API_KEY=your-zhipuai-api-key
```

## 开发说明

### 导出依赖

```bash
# 后端依赖
pip freeze > requirements.txt

# 前端依赖
npm install
```

### 数据库迁移

数据库结构变更时，需要更新`knowledge_assistant.sql`文件。

## 故障排除

1. **端口冲突**：检查8000、3000、9000端口是否被占用
2. **数据库连接失败**：确认MySQL服务运行且配置正确
3. **MinIO连接失败**：确认MinIO服务运行且网络可达
4. **依赖安装失败**：检查网络连接或使用国内镜像源

## 许可证

本项目采用MIT许可证。

## 支持

如有问题，请提交Issue或联系开发团队。
