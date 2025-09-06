from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any

from app.database.models import User, Conversation, ConversationMessage, Organization


class ConversationManager:
    def __init__(self):
        pass

    @staticmethod
    def _extract_title(question: str) -> str:
        """从问题中提取标题（前10个字符）"""
        first_question = question.split('\n---\n')[0] if '\n---\n' in question else question
        return first_question[:10] if len(first_question) <= 10 else first_question[:10] + "..."

    @staticmethod
    def create_conversation(db: Session, user_id: int, title: str = None, organization_id: int = None) -> Conversation:
        """创建新的对话记录"""
        # 如果没有提供标题，则使用默认标题
        if not title:
            title = "新的对话"
        
        print(f"在create_conversation中，title的值为{title}")
            
        # 创建一个空的对话记录
        conversation = Conversation(
            user_id=user_id,
            organization_id=organization_id,
            title=title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def update_conversation(db: Session, conversation_id: int, question: str, answer: str, 
                          user_id: int = None, organization_id: int = None) -> Conversation:
        """更新对话记录，添加新的问答对"""
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话记录不存在"
            )

        # 如果标题是默认的"新的对话"，则更新为第一个问题的前10个字符
        if conversation.title == "新的对话":
            conversation.title = ConversationManager._extract_title(question)
        
        # 创建新的对话消息记录
        message = ConversationMessage(
            conversation_id=conversation_id,
            user_id=user_id,
            organization_id=organization_id,
            question=question,
            answer=answer
        )
        
        db.add(message)
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
        return conversation


    @staticmethod
    def get_owner_conversations_title(db: Session, owner_id: int, is_user: bool = True, limit: int = 9999, offset: int = 0) -> List[Dict[str, Any]]:
        """获取所有者（用户或组织）的对话历史标题"""
        if is_user:
            # 验证用户是否存在
            user = db.query(User).filter(User.id == owner_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            conversations = db.query(Conversation)\
                .filter(Conversation.user_id == owner_id)\
                .order_by(Conversation.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
        else:
            # 验证组织是否存在
            organization = db.query(Organization).filter(Organization.id == owner_id).first()
            if not organization:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="组织不存在"
                )
            
            conversations = db.query(Conversation)\
                .filter(Conversation.organization_id == owner_id)\
                .order_by(Conversation.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
        
        return [
            {
                "id": conv.id,
                "owner_id": owner_id,
                "is_user": is_user,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(sep = " ") if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat(sep = " ") if conv.updated_at else None
            }
            for conv in conversations
        ]

    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: int, user_id: int = None) -> List[Dict[str, Any]]:
        """获取对话的所有消息"""
        messages = db.query(ConversationMessage)\
            .filter(ConversationMessage.conversation_id == conversation_id)\
            .order_by(ConversationMessage.created_at.asc())\
            .all()
        
        return [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id ,
                "question": msg.question,
                "answer": msg.answer,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    
    @staticmethod
    def get_conversation_created_time(db: Session, conversation_id: int) -> str:
        """根据conversation_id获取对应的created_time（返回字符串格式）"""
        # 查询会话是否存在
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        created_time: datetime = conversation.created_at
        # 转换为字符串（你可以选择需要的格式）
        return created_time.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_single_conversation_title(db: Session, conversation_id: int) -> str:
        """根据conversation_id获取对应的title"""
        # 查询会话是否存在
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        title = conversation.title
        # 转换为字符串（你可以选择需要的格式）
        return title

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int = None) -> bool:
        """删除对话及其所有消息"""
        # 验证对话是否存在
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话记录不存在"
            )
        
        # 删除所有消息
        db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).delete()
        
        # 删除对话
        db.delete(conversation)
        db.commit()
        return True

    @staticmethod
    def delete_message(db: Session, message_id: int, user_id: int = None, is_question: bool = False) -> bool:
        """删除单条消息或部分消息内容"""
        # 验证消息是否存在
        message = db.query(ConversationMessage).filter(ConversationMessage.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        if is_question:
            # 删除整个消息（包括问题和回答）
            db.delete(message)
        else:
            # 只删除回答，将answer字段置为空
            message.answer = ""
        
        db.commit()
        return True
