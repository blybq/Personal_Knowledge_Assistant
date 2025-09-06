from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
import logging

from app.database.models import (User, Organization, Conversation, Note, 
                NoteFolder, OrganizationMember, AdminOperations, ConversationMessage)

logger = logging.getLogger(__name__)

class AdminService:
    @staticmethod
    def is_admin(db: Session, user_id: int) -> bool:
        """检查用户是否为管理员"""
        user = db.query(User).filter(User.id == user_id).first()
        return user.is_admin if user else False

    @staticmethod
    def get_all_users(db: Session, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取所有用户信息（分页）"""
        try:
            # 计算总数
            total_count = db.query(func.count(User.id)).scalar()
            
            # 获取分页数据
            users = db.query(User).order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
            
            # 将ORM对象转换为字典
            user_list = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin,
                    "is_banned": user.is_banned,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                user_list.append(user_dict)
            
            return {
                "users": user_list,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise

    @staticmethod
    def get_all_organizations(db: Session, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取所有组织信息（分页）"""
        try:
            # 计算总数
            total_count = db.query(func.count(Organization.id)).scalar()
            
            # 获取分页数据，包含创建者信息和成员数量
            organizations = db.query(
                Organization,
                User.username.label('creator_name'),
                func.count(OrganizationMember.user_id).label('member_count')
            ).join(User, Organization.creator_id == User.id
            ).outerjoin(OrganizationMember, Organization.id == OrganizationMember.organization_id
            ).group_by(Organization.id, User.username
            ).order_by(Organization.created_at.desc()
            ).offset((page - 1) * page_size
            ).limit(page_size).all()
            
            org_list = []
            for org, creator_name, member_count in organizations:
                org_dict = {
                    "id": org.id,
                    "name": org.name,
                    "description": org.description,
                    "invite_code": org.invite_code,
                    "creator_id": org.creator_id,
                    "creator_name": creator_name,
                    "member_count": member_count,
                    "created_at": org.created_at.isoformat() if org.created_at else None,
                    "updated_at": org.updated_at.isoformat() if org.updated_at else None
                }
                org_list.append(org_dict)
            
            return {
                "organizations": org_list,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"获取组织列表失败: {e}")
            raise

    @staticmethod
    def ban_user(db: Session, admin_id: int, user_id: int, reason: str = "") -> bool:
        """封禁用户"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_banned = True
            db.commit()
            
            # 记录管理员操作
            AdminService.log_admin_operation(
                db, admin_id, 'user', user_id, 'ban_user', 
                f"封禁用户 {user.username}，原因: {reason}"
            )
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"封禁用户失败: {e}")
            return False

    @staticmethod
    def unban_user(db: Session, admin_id: int, user_id: int, reason: str = "") -> bool:
        """解封用户"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_banned = False
            db.commit()
            
            # 记录管理员操作
            AdminService.log_admin_operation(
                db, admin_id, 'user', user_id, 'unban_user', 
                f"解封用户 {user.username}，原因: {reason}"
            )
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"解封用户失败: {e}")
            return False

    @staticmethod
    def delete_organization(db: Session, admin_id: int, organization_id: int, reason: str = "") -> bool:
        """解散组织（管理员权限）"""
        try:
            organization = db.query(Organization).filter(Organization.id == organization_id).first()
            if not organization:
                return False
            
            # 先删除组织相关的数据，避免约束冲突
            # 1. 删除组织相关的对话消息
            db.query(ConversationMessage).filter(ConversationMessage.organization_id == organization_id).delete()
            
            # 2. 删除组织相关的对话
            db.query(Conversation).filter(Conversation.organization_id == organization_id).delete()
            
            # 3. 删除组织相关的笔记附件
            from database.models import NoteAttachment, Note
            # 先找到组织的所有笔记
            org_notes = db.query(Note.id).filter(Note.organization_id == organization_id).all()
            note_ids = [note.id for note in org_notes]
            if note_ids:
                db.query(NoteAttachment).filter(NoteAttachment.note_id.in_(note_ids)).delete()
            
            # 4. 删除组织相关的笔记
            db.query(Note).filter(Note.organization_id == organization_id).delete()
            
            # 5. 删除组织相关的文件夹
            db.query(NoteFolder).filter(NoteFolder.organization_id == organization_id).delete()
            
            # 6. 删除组织成员关系
            db.query(OrganizationMember).filter(OrganizationMember.organization_id == organization_id).delete()
            
            # 最后删除组织
            db.delete(organization)
            db.commit()
            
            # 记录管理员操作
            AdminService.log_admin_operation(
                db, admin_id, 'organization', organization_id, 'delete_organization', 
                f"解散组织 {organization.name}，原因: {reason}"
            )
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"解散组织失败: {e}")
            return False

    @staticmethod
    def get_user_details(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户详细信息"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # 将用户对象转换为字典
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_banned": user.is_banned,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
            # 获取用户的对话并转换为字典
            conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
            conversation_list = []
            for conv in conversations:
                conv_dict = {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                }
                conversation_list.append(conv_dict)
            
            # 获取用户的文件夹并转换为字典
            folders = db.query(NoteFolder).filter(NoteFolder.user_id == user_id).all()
            folder_list = []
            for folder in folders:
                folder_dict = {
                    "id": folder.id,
                    "name": folder.name,
                    "created_at": folder.created_at.isoformat() if folder.created_at else None,
                    "updated_at": folder.updated_at.isoformat() if folder.updated_at else None
                }
                folder_list.append(folder_dict)
            
            # 获取每个文件夹下的笔记数量
            folder_notes = {}
            for folder in folders:
                note_count = db.query(func.count(Note.id)).filter(Note.folder_id == folder.id).scalar()
                folder_notes[folder.id] = note_count
            
            # 获取用户加入的组织并转换为字典
            organizations = db.query(
                Organization, 
                OrganizationMember.is_creator
            ).join(OrganizationMember, Organization.id == OrganizationMember.organization_id
            ).filter(OrganizationMember.user_id == user_id).all()
            
            org_list = []
            for org, is_creator in organizations:
                org_dict = {
                    "id": org.id,
                    "name": org.name,
                    "description": org.description,
                    "invite_code": org.invite_code,
                    "is_creator": is_creator,
                    "created_at": org.created_at.isoformat() if org.created_at else None,
                    "updated_at": org.updated_at.isoformat() if org.updated_at else None
                }
                org_list.append(org_dict)
            
            return {
                "user": user_dict,
                "conversations": conversation_list,
                "folders": folder_list,
                "folder_notes": folder_notes,
                "organizations": org_list
            }
        except Exception as e:
            logger.error(f"获取用户详情失败: {e}")
            return {}

    @staticmethod
    def get_organization_details(db: Session, organization_id: int) -> Dict[str, Any]:
        """获取组织详细信息"""
        try:
            organization = db.query(Organization).filter(Organization.id == organization_id).first()
            if not organization:
                return {}
            
            # 将组织对象转换为字典
            org_dict = {
                "id": organization.id,
                "name": organization.name,
                "description": organization.description,
                "invite_code": organization.invite_code,
                "creator_id": organization.creator_id,
                "created_at": organization.created_at.isoformat() if organization.created_at else None,
                "updated_at": organization.updated_at.isoformat() if organization.updated_at else None
            }
            
            # 获取组织成员并转换为字典
            members = db.query(
                User, 
                OrganizationMember.is_creator
            ).join(OrganizationMember, User.id == OrganizationMember.user_id
            ).filter(OrganizationMember.organization_id == organization_id).all()
            
            member_list = []
            for user, is_creator in members:
                member_dict = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_creator": is_creator,
                    "joined_at": user.created_at.isoformat() if user.created_at else None
                }
                member_list.append(member_dict)
            
            # 获取组织的对话并转换为字典
            conversations = db.query(Conversation).filter(Conversation.organization_id == organization_id).all()
            conversation_list = []
            for conv in conversations:
                conv_dict = {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                }
                conversation_list.append(conv_dict)
            
            # 获取组织的文件夹并转换为字典
            folders = db.query(NoteFolder).filter(NoteFolder.organization_id == organization_id).all()
            folder_list = []
            for folder in folders:
                folder_dict = {
                    "id": folder.id,
                    "name": folder.name,
                    "created_at": folder.created_at.isoformat() if folder.created_at else None,
                    "updated_at": folder.updated_at.isoformat() if folder.updated_at else None
                }
                folder_list.append(folder_dict)
            
            # 获取每个文件夹下的笔记数量
            folder_notes = {}
            for folder in folders:
                note_count = db.query(func.count(Note.id)).filter(Note.folder_id == folder.id).scalar()
                folder_notes[folder.id] = note_count
            
            return {
                "organization": org_dict,
                "members": member_list,
                "conversations": conversation_list,
                "folders": folder_list,
                "folder_notes": folder_notes
            }
        except Exception as e:
            logger.error(f"获取组织详情失败: {e}")
            return {}

    @staticmethod
    def delete_user_account(db: Session, user_id: int, admin_id: int = None, reason: str = "") -> bool:
        """删除用户账号（用户自己注销或管理员操作）"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # 记录操作（如果是管理员操作）
            if admin_id:
                AdminService.log_admin_operation(
                    db, admin_id, 'user', user_id, 'delete_user', 
                    f"删除用户账号 {user.username}，原因: {reason}"
                )
            
            # 先删除用户相关的数据，避免约束冲突
            # 1. 删除用户的对话消息
            db.query(ConversationMessage).filter(ConversationMessage.user_id == user_id).delete()
            
            # 2. 删除用户的对话
            db.query(Conversation).filter(Conversation.user_id == user_id).delete()
            
            # 3. 删除用户的笔记附件
            from database.models import NoteAttachment, Note
            # 先找到用户的所有笔记
            user_notes = db.query(Note.id).filter(Note.user_id == user_id).all()
            note_ids = [note.id for note in user_notes]
            if note_ids:
                db.query(NoteAttachment).filter(NoteAttachment.note_id.in_(note_ids)).delete()
            
            # 4. 删除用户的笔记
            db.query(Note).filter(Note.user_id == user_id).delete()
            
            # 5. 删除用户的文件夹
            db.query(NoteFolder).filter(NoteFolder.user_id == user_id).delete()
            
            # 6. 删除用户从组织中移除（但不删除组织本身）
            db.query(OrganizationMember).filter(OrganizationMember.user_id == user_id).delete()
            
            # 7. 删除用户创建的组织（需要先删除组织相关的数据）
            user_created_orgs = db.query(Organization).filter(Organization.creator_id == user_id).all()
            for org in user_created_orgs:
                # 删除组织相关的对话消息
                db.query(ConversationMessage).filter(ConversationMessage.organization_id == org.id).delete()
                # 删除组织相关的对话
                db.query(Conversation).filter(Conversation.organization_id == org.id).delete()
                # 删除组织相关的笔记附件
                org_notes = db.query(Note.id).filter(Note.organization_id == org.id).all()
                org_note_ids = [note.id for note in org_notes]
                if org_note_ids:
                    db.query(NoteAttachment).filter(NoteAttachment.note_id.in_(org_note_ids)).delete()
                # 删除组织相关的笔记
                db.query(Note).filter(Note.organization_id == org.id).delete()
                # 删除组织相关的文件夹
                db.query(NoteFolder).filter(NoteFolder.organization_id == org.id).delete()
                # 删除组织成员关系
                db.query(OrganizationMember).filter(OrganizationMember.organization_id == org.id).delete()
                # 删除组织
                db.delete(org)
            
            # 最后删除用户
            db.delete(user)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"删除用户账号失败: {e}")
            return False

    @staticmethod
    def log_admin_operation(db: Session, admin_id: int, target_type: str, target_id: int, 
                           operation_type: str, operation_details: str = "") -> None:
        """记录管理员操作日志"""
        try:
            operation = AdminOperations(
                admin_id=admin_id,
                target_type=target_type,
                target_id=target_id,
                operation_type=operation_type,
                description=operation_details
            )
            db.add(operation)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"记录管理员操作日志失败: {e}")

    @staticmethod
    def get_admin_operations(db: Session, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """获取管理员操作日志（分页）"""
        try:
            # 计算总数
            total_count = db.query(func.count(AdminOperations.id)).scalar()
            
            # 获取分页数据，包含管理员用户名
            operations = db.query(
                AdminOperations,
                User.username.label('admin_username')
            ).join(User, AdminOperations.admin_id == User.id
            ).order_by(desc(AdminOperations.created_at)
            ).offset((page - 1) * page_size
            ).limit(page_size).all()
            
            op_list = []
            for op, admin_username in operations:
                op_dict = {
                    "id": op.id,
                    "admin_id": op.admin_id,
                    "admin_username": admin_username,
                    "operation_type": op.operation_type,
                    "target_type": op.target_type,
                    "target_id": op.target_id,
                    "description": op.description,
                    "created_at": op.created_at.isoformat() if op.created_at else None
                }
                op_list.append(op_dict)
            
            return {
                "operations": op_list,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        except Exception as e:
            logger.error(f"获取管理员操作日志失败: {e}")
            return {"operations": [], "total_count": 0, "page": page, "page_size": page_size, "total_pages": 0}
