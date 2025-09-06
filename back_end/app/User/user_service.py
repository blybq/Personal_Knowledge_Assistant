from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.models import User, Conversation
from typing import Optional
import hashlib

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> dict:
        """创建新用户"""
        try:
            # 检查用户名或邮箱是否已存在
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return {
                    "success": False, 
                    "message": "用户名或邮箱已存在"
                }
            
            # 创建新用户
            hashed_password = UserService.hash_password(password)
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {
                "success": True,
                "message": "用户创建成功",
                "data": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "created_at": new_user.created_at.isoformat() if new_user.created_at else None
                }
            }
        except IntegrityError as e:
            db.rollback()
            return {
                "success": False,
                "message": "数据库错误: " + str(e.orig)
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": "创建用户时发生错误: " + str(e)
            }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_username(db: Session, user_id: int, new_username: str) -> dict:
        """更新用户名"""
        try:
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == new_username).first()
            if existing_user and existing_user.id != user_id:
                return {
                    "success": False, 
                    "message": "用户名已存在"
                }
            
            # 更新用户名
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": "用户不存在"
                }
            
            user.username = new_username
            db.commit()
            db.refresh(user)
            
            return {
                "success": True,
                "message": "用户名更新成功",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": "更新用户名时发生错误: " + str(e)
            }

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> dict:
        """更新用户密码"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "success": False,
                    "message": "用户不存在"
                }
            
            # 对新密码进行哈希处理
            hashed_password = UserService.hash_password(new_password)
            user.hashed_password = hashed_password
            db.commit()
            
            return {
                "success": True,
                "message": "密码更新成功",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": "更新密码时发生错误: " + str(e)
            }
