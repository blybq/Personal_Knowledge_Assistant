from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid
import os
from typing import List, Optional
from app.database.models import SessionLocal
from app.database.models import Note, NoteFolder, NoteAttachment
from .minio_service import minio_service

import urllib.parse
from urllib.parse import urlparse

class NoteService:
    def __init__(self, db: Session):
        self.db = db
    
    # 笔记相关操作
    def create_note(self, title: str, content: str, user_id: Optional[int] = None, 
                   organization_id: Optional[int] = None, folder_id: Optional[int] = None) -> Note:
        note = Note(
            title=title,
            content=content,
            user_id=user_id,
            organization_id=organization_id,
            folder_id=folder_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note
    
    def get_note_by_id(self, note_id: int, user_id: Optional[int] = None) -> Optional[Note]:
        query = self.db.query(Note).filter(Note.id == note_id)
        # if user_id is not None:
        #     query = query.filter(Note.user_id == user_id)
        return query.first()
    
    def get_user_notes(self, user_id: int, folder_id: Optional[int] = None) -> List[Note]:
        query = self.db.query(Note).filter(Note.user_id == user_id)
        if folder_id:
            query = query.filter(Note.folder_id == folder_id)
        return query.order_by(Note.updated_at.desc()).all()
    
    def get_notes_by_folder(self, folder_id: Optional[int] = None) -> List[Note]:
        """根据文件夹ID获取笔记列表（不需要user_id，因为folder_id已经是唯一的）"""
        query = self.db.query(Note)
        if folder_id:
            query = query.filter(Note.folder_id == folder_id)
        else:
            query = query.filter(Note.folder_id.is_(None))
        return query.order_by(Note.updated_at.desc()).all()
    
    def update_note(self, note_id: int, **kwargs) -> Optional[Note]:
        note = self.get_note_by_id(note_id)
        if note:
            for key, value in kwargs.items():
                if hasattr(note, key) and value is not None:
                    setattr(note, key, value)
            note.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(note)
        return note
    
    def delete_note(self, note_id: int) -> bool:
        note = self.get_note_by_id(note_id)
        if note:
            # 先获取所有附件
            attachments = self.get_note_attachments(note_id)
            
            # 删除所有附件（包括MinIO中的文件）
            for attachment in attachments:
                self.delete_attachment(attachment.id)
            
            # 删除笔记
            self.db.delete(note)
            self.db.commit()
            
            # 删除MinIO中的笔记目录
            try:                
                minio_service.delete_note_directory(note.user_id, note.organization_id, note.folder_id or 0, note_id)
            except Exception as e:
                print(f"Error deleting note directory from MinIO: {e}")
            
            return True
        return False
    
    # 文件夹相关操作
    def create_folder(self, name: str, user_id: Optional[int] = None, 
                     organization_id: Optional[int] = None) -> NoteFolder:
        folder = NoteFolder(
            name=name,
            user_id=user_id,
            organization_id=organization_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder
    
    def get_folder_by_id(self, folder_id: int) -> Optional[NoteFolder]:
        return self.db.query(NoteFolder).filter(NoteFolder.id == folder_id).first()
    
    def get_user_folders(self, user_id: int) -> List[NoteFolder]:
        """获取用户的所有文件夹（不再支持多级文件夹）"""
        return self.db.query(NoteFolder).filter(
            NoteFolder.user_id == user_id
        ).order_by(NoteFolder.name).all()

    def get_organization_folders(self, organization_id: int) -> List[NoteFolder]:
        """获取组织的所有文件夹"""
        return self.db.query(NoteFolder).filter(
            NoteFolder.organization_id == organization_id
        ).order_by(NoteFolder.name).all()

    def get_organization_notes(self, organization_id: int, folder_id: Optional[int] = None) -> List[Note]:
        """获取组织的所有笔记"""
        query = self.db.query(Note).filter(Note.organization_id == organization_id)
        if folder_id:
            query = query.filter(Note.folder_id == folder_id)
        return query.order_by(Note.updated_at.desc()).all()
    
    def update_folder(self, folder_id: int, user_id: int, **kwargs) -> Optional[NoteFolder]:
        folder = self.get_folder_by_id(folder_id, user_id)
        if folder:
            for key, value in kwargs.items():
                if hasattr(folder, key) and value is not None:
                    setattr(folder, key, value)
            folder.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(folder)
        return folder
    
    def delete_folder(self, folder_id: int) -> bool:
        folder = self.get_folder_by_id(folder_id)
        if folder:
            # 获取文件夹中的所有笔记
            notes = self.get_notes_by_folder(folder_id)
            
            # 递归删除所有笔记（包括附件和MinIO中的文件）
            for note in notes:
                self.delete_note(note.id)
            
            # 删除MinIO中的文件夹目录
            try:
                minio_service.delete_folder_directory(folder.user_id, folder.organization_id, folder_id)
            except Exception as e:
                print(f"Error deleting folder directory from MinIO: {e}")
            
            # 删除文件夹
            self.db.delete(folder)
            self.db.commit()
            return True
        return False
    
    # 附件相关操作
    def create_attachment(self, note_id: int, file_name: str, file_url: str, 
                         mime_type: str, size: int) -> NoteAttachment:
        attachment = NoteAttachment(
            note_id=note_id,
            file_name=file_name,
            file_url=file_url,
            mime_type=mime_type,
            size=size,
            created_at=datetime.utcnow()
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment
    
    def get_note_attachments(self, note_id: int) -> List[NoteAttachment]:
        return self.db.query(NoteAttachment).filter(
            NoteAttachment.note_id == note_id
        ).order_by(NoteAttachment.created_at.asc()).all()
    
    def get_attachment_by_id(self, attachment_id: int) -> Optional[NoteAttachment]:
        return self.db.query(NoteAttachment).filter(
            NoteAttachment.id == attachment_id
        ).first()
    
    def delete_attachment(self, attachment_id: int) -> bool:
        attachment = self.get_attachment_by_id(attachment_id)
        if attachment:
            # 从MinIO中删除文件
            try:
                # 从URL中提取文件名（URL格式：http://minio/notes/user_1/folder_0/note_1/filename.ext）
                # 我们需要提取object name部分

                
                parsed_url = urlparse(attachment.file_url)
                # object name是路径部分去掉开头的斜杠
                object_name = parsed_url.path.lstrip('/notes')
                
                # 删除MinIO中的文件
                minio_service.client.remove_object(minio_service.bucket_name, object_name)
            except Exception as e:
                print(f"Error deleting file from MinIO: {e}")
            
            # 删除数据库记录
            self.db.delete(attachment)
            self.db.commit()
            return True
        return False

# 获取笔记服务实例
def get_note_service():
    db = SessionLocal()
    try:
        yield NoteService(db)
    finally:
        db.close()
