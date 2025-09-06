from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import jwt
import os

from app.database.models import User, Conversation
from app.Conversation.conversation_manager import ConversationManager
from app.User.user_service import UserService


class SessionManager:
    # JWT配置
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """创建JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SessionManager.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SessionManager.SECRET_KEY, algorithm=SessionManager.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def authenticate_user(db: Session, email: str = None, password: str = None, user_id: int = None) -> User:
        """验证用户凭据"""
        if user_id:
            # 通过用户ID验证
            user = db.query(User).filter(User.id == user_id).first()
        elif email:
            # 通过邮箱验证
            user = db.query(User).filter(User.email == email).first()
        else:
            return None
        
        if not user:
            return None
        
        # 验证密码
        if password:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if user.hashed_password != hashed_password:
                return None
            
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """用户登录并获取对话历史"""
        # 验证用户凭据
        user = SessionManager.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 生成JWT token
        access_token = SessionManager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 构造返回数据
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "is_admin": user.is_admin
        }
        
        # 获取用户对话历史标题
        conversations_title = ConversationManager.get_owner_conversations_title(db, user.id, True, limit=9999, offset=0)
        
        return {
            "success": True,
            "message": "登录成功",
            "token": access_token,
            "data": {
                "user": user_data,
                "conversations": conversations_title
            }
        }

    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str) -> dict:
        """用户注册功能"""
        # 调用UserService的create_user方法实现用户注册
        return UserService.create_user(db, username, email, password)



    @staticmethod
    def create_conversation(db: Session, user_id: int, title: str = None) -> Conversation:
        """创建新的对话记录"""
        return ConversationManager.create_conversation(db, user_id, title)

    # @staticmethod
    # def update_conversation(db: Session, conversation_id: int, question: str, answer: str) -> Conversation:
    #     """更新对话记录，添加新的问答对"""
    #     return ConversationManager.update_conversation(db, conversation_id, question, answer)
