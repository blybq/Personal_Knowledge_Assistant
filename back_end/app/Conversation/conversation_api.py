from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.models import get_db, Conversation, ConversationMessage
from app.Conversation.conversation_manager import ConversationManager

router = APIRouter(prefix="/api", tags=["conversations"])

# Pydantic模型类
class NewConversationRequest(BaseModel):
    owner_id: int
    is_user: bool = True  # True表示用户账号，False表示组织账号

class NewConversationResponse(BaseModel):
    success: bool
    data: dict = None

class ConversationHistoryResponse(BaseModel):
    success: bool
    data: list = None

class ConversationDetailResponse(BaseModel):
    success: bool
    data: dict = None

@router.post("/conversations/new", response_model=NewConversationResponse)
def create_new_conversation(request: NewConversationRequest, db: Session = Depends(get_db)):
    """创建新的对话"""
    if request.is_user:
        result = ConversationManager.create_conversation(db, request.owner_id, organization_id=None)
    else:
        result = ConversationManager.create_conversation(db, user_id=None, organization_id=request.owner_id)
    
    return NewConversationResponse(
        success=True,
        data={
            "id": result.id,
            "title": result.title,
            "owner_id": request.owner_id,
            "is_user": request.is_user
        }
    )

class ConversationDetailRequest(BaseModel):
    owner_id: int
    is_user: bool = True

@router.get("/conversations/history", response_model=ConversationHistoryResponse)
def get_conversation_history_title( 
    owner_id: int,
    is_user: bool,
    limit: int,
    offset: int,
    db: Session = Depends(get_db)):

    # is_user_bool = True if is_user == "true" else False

    """获取所有者（用户或组织）的对话历史标题"""
    title = ConversationManager.get_owner_conversations_title(
        db, owner_id, is_user, limit, offset
    )
    return ConversationHistoryResponse(
        success=True,
        data=title
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int, 
    owner_id: int,
    is_user: bool,
    db: Session = Depends(get_db)):
    """获取指定对话记录"""
    # 首先验证权限
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # is_user_bool = True if is_user == "true" else False
    
    # 检查权限
    if is_user:
        if conversation.user_id != owner_id:
            raise HTTPException(status_code=403, detail="无权访问此对话")
    else:
        if conversation.organization_id != owner_id:
            raise HTTPException(status_code=403, detail="无权访问此对话")
    
    # 获取对话的所有消息
    messages = ConversationManager.get_conversation_messages(db, conversation_id, None)
    title = ConversationManager.get_single_conversation_title(db, conversation_id)
    created_time = ConversationManager.get_conversation_created_time(db, conversation_id)
    
    return ConversationDetailResponse(
        success=True,
        data={
            "id": conversation_id,
            "title": title,
            "messages": messages,
            "created_at": created_time,
            "owner_id": owner_id,
            "is_user": is_user
        }
    )



class DeleteConversationRequest(BaseModel):
    owner_id: int
    is_user: bool = True

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int,  
            owner_id: int,
            is_user: bool,
            db: Session = Depends(get_db)):
    """删除对话及其所有消息"""
    # 首先验证权限
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查权限
    if is_user:
        if conversation.user_id != owner_id:
            raise HTTPException(status_code=403, detail="无权删除此对话")
    else:
        if conversation.organization_id != owner_id:
            raise HTTPException(status_code=403, detail="无权删除此对话")
    
    success = ConversationManager.delete_conversation(db, conversation_id, None)
    return {
        "success": success,
        "message": "删除对话成功" if success else "删除对话失败"
    }

class DeleteMessageRequest(BaseModel):
    owner_id: int
    is_user: bool = True
    is_question: bool = False

@router.delete("/messages/{message_id}")
def delete_message(message_id: int, 
            owner_id: int,
            is_user: bool,
            is_question: bool,
            db: Session = Depends(get_db)):
    """删除单条消息或部分消息内容"""
    # 首先验证权限
    message = db.query(ConversationMessage).filter(ConversationMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 检查权限
    if is_user:
        if conversation.user_id != owner_id:
            raise HTTPException(status_code=403, detail="无权删除此消息")
    else:
        if conversation.organization_id != owner_id:
            raise HTTPException(status_code=403, detail="无权删除此消息")
    
    success = ConversationManager.delete_message(db, message_id, None, is_question)
    return {
        "success": success,
        "message": "删除消息成功" if success else "删除消息失败"
    }
