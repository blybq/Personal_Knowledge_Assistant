from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from typing import Optional
import pytz

# from Config.config import database_url

# 数据库配置
# DATABASE_URL = database_url
database_url = os.getenv("DATABASE_URL")

# 创建数据库引擎
engine = create_engine(database_url, echo=True)# 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

beijing = pytz.timezone("Asia/Shanghai")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)  # 管理员标识
    is_banned = Column(Boolean, default=False)  # 封禁标识
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联对话历史
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 改为可为空，支持组织账号
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # 新增组织ID
    title = Column(String(100), nullable=True)  # 增加标题长度
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联用户
    user = relationship("User", back_populates="conversations")
    
    # 关联组织
    organization = relationship("Organization")
    
    # 关联对话消息
    messages = relationship("ConversationMessage", back_populates="conversation")
    
    # 检查约束：user_id 和 organization_id 不能同时为空，且不能同时不为空
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL AND organization_id IS NULL) OR (user_id IS NULL AND organization_id IS NOT NULL)', 
                       name='chk_conversation_owner'),
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 改为可为空，支持组织账号
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # 新增组织ID
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联对话
    conversation = relationship("Conversation", back_populates="messages")
    
    # 关联用户
    user = relationship("User")
    
    # 关联组织
    organization = relationship("Organization")
    
    # 检查约束：user_id 和 organization_id 不能同时为空，且不能同时不为空
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL AND organization_id IS NULL) OR (user_id IS NULL AND organization_id IS NOT NULL)', 
                       name='chk_conversation_message_owner'),
    )




class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 改为可为空，支持组织账号
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # 新增组织ID
    folder_id = Column(Integer, ForeignKey("note_folders.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联用户
    user = relationship("User")
    # 关联组织
    organization = relationship("Organization")
    # 关联文件夹
    folder = relationship("NoteFolder")
    # 关联附件
    attachments = relationship("NoteAttachment", back_populates="note", cascade="all, delete-orphan")
    
    # 检查约束：user_id 和 organization_id 不能同时为空，且不能同时不为空
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL AND organization_id IS NULL) OR (user_id IS NULL AND organization_id IS NOT NULL)', 
                       name='chk_note_owner'),
    )


class NoteFolder(Base):
    __tablename__ = "note_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 改为可为空，支持组织账号
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # 新增组织ID
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联用户
    user = relationship("User")
    # 关联组织
    organization = relationship("Organization")
    # 关联笔记
    notes = relationship("Note", back_populates="folder")
    
    # 检查约束：user_id 和 organization_id 不能同时为空，且不能同时不为空
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL AND organization_id IS NULL) OR (user_id IS NULL AND organization_id IS NOT NULL)', 
                       name='chk_note_folder_owner'),
    )


class NoteAttachment(Base):
    __tablename__ = "note_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)  # 文件大小（字节）
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    
    # 关联笔记
    note = relationship("Note", back_populates="attachments")


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    invite_code = Column(String(50), unique=True, index=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联创建者
    creator = relationship("User")
    
    # 关联成员
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_creator = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(beijing))
    
    # 关联用户
    user = relationship("User")
    
    # 关联组织
    organization = relationship("Organization", back_populates="members")
    
    # 唯一约束：一个用户在一个组织中只能有一个成员记录
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization'),
    )




class AdminOperations(Base):
    __tablename__ = "admin_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment='操作的管理员ID')
    target_type = Column(Enum('user', 'organization', name='target_type_enum'), nullable=False, comment='操作目标类型')
    target_id = Column(Integer, nullable=False, comment='操作目标ID')
    operation_type = Column(String(50), nullable=False, comment='操作类型（ban_user, unban_user, delete_organization等）')
    description = Column(Text, comment='操作详情')
    created_at = Column(DateTime, default=lambda: datetime.now(beijing))
    updated_at = Column(DateTime, default=lambda: datetime.now(beijing), onupdate=lambda: datetime.now(beijing))
    
    # 关联管理员用户
    admin = relationship("User")
    
    # 添加索引
    __table_args__ = (
        Index('idx_admin_id', 'admin_id'),
        Index('idx_target_type_target_id', 'target_type', 'target_id'),
        Index('idx_created_at', 'created_at'),
    )


# 创建表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
