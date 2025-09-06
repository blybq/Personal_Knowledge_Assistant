from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.database.models import get_db
from app.notes.notes_service import NoteService, get_note_service
from app.notes.minio_service import minio_service

# Pydantic模型类
class NoteCreateRequest(BaseModel):
    title: str
    content: str = ""
    owner_id: int
    is_user: bool = True
    folder_id: Optional[int] = None

class NoteUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[int] = None

class FolderCreateRequest(BaseModel):
    name: str
    owner_id: int
    is_user: bool = True

# class NoteDeleteRequest(BaseModel):
#     user_id: int

class FolderDeleteRequest(BaseModel):
    owner_id: int
    is_user: bool = True

class AttachmentUploadRequest(BaseModel):
    owner_id: int
    is_user: bool = True

class AttachmentGetRequest(BaseModel):
    owner_id: int
    is_user: bool = True

# class AttachmentDeleteRequest(BaseModel):
#     user_id: int

class FoldersGetRequest(BaseModel):
    owner_id: int
    is_user: bool = True

router = APIRouter(prefix="/api/notes", tags=["notes"])

# 笔记相关接口
@router.get("/titles")
async def get_note_titles(
    folder_id: Optional[int] = None,
    note_service: NoteService = Depends(get_note_service)
):
    """获取笔记标题列表"""
    # 这里需要修改notes_service.get_user_notes方法，使其不需要user_id参数
    # 因为folder_id已经是唯一的，可以直接根据folder_id查询
    notes = note_service.get_notes_by_folder(folder_id)
    return {
        "success": True,
        "message": "获取笔记列表成功",
        "data": [
            {
                "id": note.id,
                "title": note.title,
                "folder_id": note.folder_id,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in notes
        ]
    }

@router.get("/{note_id}/detail")
async def get_note_detail(
    note_id: int,
    note_service: NoteService = Depends(get_note_service)
):
    """获取笔记详情"""
    note = note_service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 获取附件列表
    attachments = note_service.get_note_attachments(note_id)
    
    return {
        "success": True,
        "message": "获取笔记详情成功",
        "data": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "folder_id": note.folder_id,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
            "attachments": [
                {
                    "id": att.id,
                    "note_id": att.note_id,
                    "file_name": att.file_name,
                    "file_url": att.file_url,
                    "mime_type": att.mime_type,
                    "size": att.size,
                    "created_at": att.created_at.isoformat()
                }
                for att in attachments
            ]
        }
    }

@router.post("")
async def create_note(
    request: NoteCreateRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """创建新笔记"""
    if request.is_user:
        note = note_service.create_note(
            request.title, 
            request.content, 
            user_id=request.owner_id, 
            organization_id=None,
            folder_id=request.folder_id
        )
    else:
        note = note_service.create_note(
            request.title, 
            request.content, 
            user_id=None, 
            organization_id=request.owner_id,
            folder_id=request.folder_id
        )
    return {
        "success": True,
        "message": "创建笔记成功",
        "data": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "folder_id": note.folder_id,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }

@router.put("/{note_id}")
async def update_note(
    note_id: int,
    request: NoteUpdateRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """更新笔记"""
    update_data = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.content is not None:
        update_data["content"] = request.content
    if request.folder_id is not None:
        update_data["folder_id"] = request.folder_id
    
    note = note_service.update_note(note_id, **update_data)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    return {
        "success": True,
        "message": "更新笔记成功",
        "data": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "folder_id": note.folder_id,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    # request: NoteDeleteRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """删除笔记"""
    success = note_service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    return {
        "success": True,
        "message": "删除笔记成功"
    }

# 文件夹相关接口
@router.get("/folders")
async def get_folders(
    owner_id: int,
    is_user: bool = True,
    note_service: NoteService = Depends(get_note_service)
):
    """获取文件夹列表"""
    if is_user:
        folders = note_service.get_user_folders(owner_id)
        # 获取每个文件夹的笔记数量
        folders_with_count = []
        for folder in folders:
            notes_count = len(note_service.get_user_notes(owner_id, folder.id))
            folders_with_count.append({
                "id": folder.id,
                "name": folder.name,
                "created_at": folder.created_at.isoformat(),
                "updated_at": folder.updated_at.isoformat(),
                "notes_count": notes_count
            })
    else:
        folders = note_service.get_organization_folders(owner_id)
        # 获取每个文件夹的笔记数量
        folders_with_count = []
        for folder in folders:
            notes_count = len(note_service.get_organization_notes(owner_id, folder.id))
            folders_with_count.append({
                "id": folder.id,
                "name": folder.name,
                "created_at": folder.created_at.isoformat(),
                "updated_at": folder.updated_at.isoformat(),
                "notes_count": notes_count
            })
    
    return {
        "success": True,
        "message": "获取文件夹列表成功",
        "data": folders_with_count
    }

@router.post("/folders")
async def create_folder(
    request: FolderCreateRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """创建文件夹"""
    if request.is_user:
        folder = note_service.create_folder(
            request.name, 
            user_id=request.owner_id, 
            organization_id=None
        )
    else:
        folder = note_service.create_folder(
            request.name, 
            user_id=None, 
            organization_id=request.owner_id
        )
    return {
        "success": True,
        "message": "创建文件夹成功",
        "data": {
            "id": folder.id,
            "name": folder.name,
            "created_at": folder.created_at.isoformat(),
            "updated_at": folder.updated_at.isoformat()
        }
    }

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    # request: FolderDeleteRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """删除文件夹"""
    success = note_service.delete_folder(folder_id)
    if not success:
        raise HTTPException(status_code=400, detail="文件夹不为空或不存在")
    
    return {
        "success": True,
        "message": "删除文件夹成功"
    }

# 附件相关接口
@router.post("/{note_id}/attachments")
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    note_service: NoteService = Depends(get_note_service)
):
    """上传附件到MinIO"""
    # 检查笔记是否存在
    note = note_service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # 上传文件到MinIO
    try:
        # 读取文件内容
        # file_content = await file.read()
        # file_size = len(file_content)
        file_size = file.size
        file_content = await file.read(file_size)
        
        # 确保笔记目录存在
        # minio_service.create_note_directory(note.user_id, note.folder_id or 0, note_id)
        
        # 上传到MinIO
        download_url = minio_service.upload_file(
            user_id=note.user_id,
            organization_id=note.organization_id,
            folder_id=note.folder_id or 0,
            note_id=note_id,
            file_name=unique_filename,
            file_data=file_content,
            file_size=file_size,
            content_type=file.content_type
        )
        
        # 创建附件记录
        attachment = note_service.create_attachment(
            note_id=note_id,
            file_name=file.filename,
            file_url=download_url,
            mime_type=file.content_type,
            size=file_size
        )
        
        return {
            "success": True,
            "message": "上传附件成功",
            "data": {
                "id": attachment.id,
                "note_id": attachment.note_id,
                "file_name": attachment.file_name,
                "file_url": attachment.file_url,
                "mime_type": attachment.mime_type,
                "size": attachment.size,
                "created_at": attachment.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/{note_id}/attachments")
async def get_attachments(
    note_id: int,
    note_service: NoteService = Depends(get_note_service)
):
    """获取笔记附件列表"""
    # 检查笔记是否存在
    note = note_service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    
    attachments = note_service.get_note_attachments(note_id)
    
    return {
        "success": True,
        "message": "获取附件列表成功",
        "data": [
            {
                "id": att.id,
                "note_id": att.note_id,
                "file_name": att.file_name,
                "file_url": att.file_url,
                "mime_type": att.mime_type,
                "size": att.size,
                "created_at": att.created_at.isoformat()
            }
            for att in attachments
        ]
    }

@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    # request: AttachmentDeleteRequest,
    note_service: NoteService = Depends(get_note_service)
):
    """删除附件"""
    attachment = note_service.get_attachment_by_id(attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    # 检查附件所属的笔记是否属于当前用户
    note = note_service.get_note_by_id(attachment.note_id)
    if not note:
        raise HTTPException(status_code=403, detail="无权操作此附件")
    
    try:
        # 删除附件（包括MinIO中的文件）
        success = note_service.delete_attachment(attachment_id)
        
        return {
            "success": success,
            "message": "删除附件成功" if success else "删除附件失败"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")
