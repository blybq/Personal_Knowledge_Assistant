# 部署指南

## 概述

本文档提供个人知识助手项目的详细部署指南，包括本地开发环境部署、Docker容器化部署和云服务器生产环境部署。

## 部署方式选择

### 1. 本地开发环境部署

适合开发调试，使用本地安装的依赖服务

### 2. Docker容器化部署  

适合测试和生产环境，使用Docker容器管理所有服务

### 3. 云服务器生产部署

适合正式生产环境，使用云服务提供商的基础设施

## 环境要求

### 硬件要求

- **CPU**: 4核以上（推荐8核）
- **内存**: 8GB以上（推荐16GB）
- **存储**: 50GB以上可用空间
- **网络**: 稳定的网络连接

### 软件要求

- **操作系统**: Ubuntu 20.04+/CentOS 7+/Windows 10+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.8+
- **Node.js**: 16+

## 本地开发环境部署

### 后端服务部署

1. **创建虚拟环境**

   ```bash
   cd back_end
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**

   ```bash
   cp .env.example .env
   # 编辑.env文件配置数据库连接等参数
   ```

4. **启动服务**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 前端服务部署

1. **安装依赖**

   ```bash
   cd front_end
   npm install
   ```

2. **启动开发服务器**

   ```bash
   npm run dev
   ```

### 数据库服务

1. **安装MySQL**

   ```bash
   # Ubuntu
   sudo apt install mysql-server
   
   # CentOS
   sudo yum install mysql-server
   ```

2. **创建数据库**

   ```sql
   CREATE DATABASE knowledge_assistant;
   ```

3. **导入数据库结构**

   ```bash
   mysql -u root -p knowledge_assistant < scripts/knowledge_assistant.sql
   ```

### MinIO对象存储

1. **下载MinIO**

   ```bash
   wget https://dl.min.io/server/minio/release/linux-amd64/minio
   chmod +x minio
   ```

2. **启动MinIO**

   ```bash
   ./minio server data
   ```

## Docker容器化部署

### 使用Docker Compose部署

1. **一键部署**

   ```bash
   # 使用部署脚本
   bash scripts/deploy.sh
   
   # 或手动部署
   docker-compose -f docker/docker-compose.yml up -d --build
   ```

2. **查看服务状态**

   ```bash
   docker-compose -f docker/docker-compose.yml ps
   ```

3. **查看日志**

   ```bash
   docker-compose -f docker/docker-compose.yml logs -f
   ```

### 服务访问地址

| 服务 | 访问地址 | 默认凭据 |
|------|----------|----------|
| 前端界面 | <http://localhost> | - |
| 后端API | <http://localhost:8000> | - |
| API文档 | <http://localhost:8000/docs> | - |
| MinIO控制台 | <http://localhost:9001> | minioadmin/minioadmin |
| MySQL数据库 | localhost:3306 | user/password |

## 云服务器生产部署

### 服务器准备

1. **购买云服务器**
   - 推荐配置: 4核8GB内存
   - 系统: Ubuntu 20.04 LTS

2. **安全组配置**
   - 开放端口: 80, 443, 8000, 9000, 9001
   - 限制SSH端口访问

3. **域名解析**
   - 将域名解析到服务器IP
   - 配置SSL证书

### 环境配置

1. **安装Docker**

   ```bash
   # Ubuntu
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

2. **部署项目**

   ```bash
   git clone <项目地址>
   cd Personal_Knowledge_Assistant
   bash scripts/deploy.sh
   ```

### Nginx配置

1. **创建Nginx配置**

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
       }
   }
   ```

2. **配置SSL证书**

   ```bash
   # 使用Certbot获取SSL证书
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## 数据库迁移

### 从开发环境迁移到生产环境

1. **导出开发环境数据**

   ```bash
   mysqldump -u root -p knowledge_assistant > backup.sql
   ```

2. **导入到生产环境**

   ```bash
   mysql -u user -p knowledge_assistant < backup.sql
   ```

### 数据库备份策略

1. **自动备份脚本**

   ```bash
   # 创建每日备份脚本
   mysqldump -u user -p password knowledge_assistant > /backup/db-$(date +%Y%m%d).sql
   ```

2. **保留策略**
   - 保留最近7天备份
   - 每周全量备份
   - 每月归档备份

## 监控和维护

### 服务监控

1. **使用Docker监控**

   ```bash
   docker stats
   docker logs <container_name>
   ```

2. **系统监控**

   ```bash
   # 监控CPU、内存、磁盘使用情况
   top
   htop
   df -h
   ```

### 日志管理

1. **查看日志**

   ```bash
   # Docker容器日志
   docker-compose logs -f
   
   # 应用日志
   tail -f back_end/app.log
   ```

2. **日志轮转**
   - 配置logrotate管理日志文件
   - 定期清理旧日志

### 性能优化

1. **数据库优化**

   ```sql
   -- 添加索引
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_conversations_user_id ON conversations(user_id);
   ```

2. **缓存优化**
   - 考虑添加Redis缓存
   - 静态资源CDN加速

## 故障排除

### 常见问题

1. **端口冲突**

   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8000
   
   # 停止占用进程
   kill <pid>
   ```

2. **数据库连接失败**
   - 检查MySQL服务状态
   - 验证连接参数
   - 检查防火墙设置

3. **依赖安装失败**

   ```bash
   # 清理缓存重试
   pip cache purge
   npm cache clean --force
   ```

### 获取帮助

1. **查看文档**
   - API文档: <http://localhost:8000/docs>
   - 本项目README.md

2. **问题排查**
   - 检查日志文件
   - 验证环境配置
   - 测试网络连接

## 更新和升级

### 版本更新

1. **拉取最新代码**

   ```bash
   git pull origin main
   ```

2. **重建服务**

   ```bash
   docker-compose -f docker/docker-compose.yml up -d --build
   ```

3. **执行迁移脚本**

   ```bash
   # 如果有数据库结构变更
   mysql -u user -p knowledge_assistant < migration_script.sql
   ```

## 安全建议

### 生产环境安全

1. **修改默认密码**
   - MySQL root密码
   - MinIO访问密钥
   - JWT密钥

2. **防火墙配置**
   - 只开放必要端口
   - 限制IP访问范围

3. **定期更新**
   - 系统安全更新
   - 依赖包版本更新

### 数据备份

1. **定期备份**
   - 数据库每日备份
   - 重要文件备份
   - 配置信息备份

2. **备份验证**
   - 定期测试备份恢复
   - 多地点备份存储
