#!/bin/bash

# 个人知识助手部署脚本
set -e

echo "🚀 开始部署个人知识助手..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 切换到脚本所在目录的上级目录
cd "$(dirname "$0")/.."

# 构建和启动服务
echo "📦 构建和启动Docker服务..."
docker-compose -f docker/docker-compose.yml up -d --build

echo "✅ 部署完成！"
echo ""
echo "📊 服务访问信息："
echo "  前端界面: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  MinIO控制台: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)"
echo "  MySQL数据库: localhost:3306 (数据库: knowledge_assistant)"
echo ""
echo "🔧 常用命令："
echo "  查看日志: docker-compose -f docker/docker-compose.yml logs -f"
echo "  停止服务: docker-compose -f docker/docker-compose.yml down"
echo "  重启服务: docker-compose -f docker/docker-compose.yml restart"
