# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from Config.config import database_url
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 变量配置
database_url = os.getenv("DATABASE_URL")

# 创建数据库引擎
engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境最好改成 ["http://localhost:3000"] 这样的精确地址
    allow_credentials=True,
    allow_methods=["*"],   # 允许的方法，比如 ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],   # 允许的请求头
)

# 导入并注册各个模块的API路由
from app.User.user_api import router as user_router
from app.User.auth_api import router as auth_router
from app.User.admin_api import router as admin_router
from app.ask_question.ask_api import router as ask_router
from app.Conversation.conversation_api import router as conversation_router
from app.notes.notes_api import router as notes_router
from app.organization.organization_api import router as organization_router

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(ask_router)
app.include_router(conversation_router)
app.include_router(notes_router)
app.include_router(organization_router)
