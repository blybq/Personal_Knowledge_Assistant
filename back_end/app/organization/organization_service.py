from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.database.models import Organization, OrganizationMember, User
from app.database.models import SessionLocal

class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_organization(self, name: str, description: str, creator_id: int) -> Organization:
        """创建新的组织"""
        # 生成唯一的邀请码
        invite_code = self._generate_unique_invite_code()
        
        organization = Organization(
            name=name,
            description=description,
            invite_code=invite_code,
            creator_id=creator_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.db.add(organization)
        self.db.flush()  # 获取组织ID
        
        # 添加创建者为组织成员
        member = OrganizationMember(
            user_id=creator_id,
            organization_id=organization.id,
            is_creator=True,
            joined_at=datetime.now()
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(organization)
        
        return organization
    
    def get_organization_by_id(self, organization_id: int) -> Optional[Organization]:
        """根据ID获取组织信息"""
        return self.db.query(Organization).filter(Organization.id == organization_id).first()
    
    def get_organization_by_invite_code(self, invite_code: str) -> Optional[Organization]:
        """根据邀请码获取组织信息"""
        return self.db.query(Organization).filter(Organization.invite_code == invite_code).first()
    
    def update_organization(self, organization_id: int, name: str, description: str) -> Optional[Organization]:
        """更新组织信息"""
        organization = self.get_organization_by_id(organization_id)
        if organization:
            organization.name = name
            organization.description = description
            organization.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(organization)
        return organization
    
    def delete_organization(self, organization_id: int) -> bool:
        """删除组织"""
        organization = self.get_organization_by_id(organization_id)
        if organization:
            self.db.delete(organization)
            self.db.commit()
            return True
        return False
    
    def join_organization(self, user_id: int, organization_id: int) -> bool:
        """用户加入组织"""
        # 检查是否已经是成员
        existing_member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id
            )
        ).first()
        
        if existing_member:
            return False  # 已经是成员
        
        member = OrganizationMember(
            user_id=user_id,
            organization_id=organization_id,
            is_creator=False,
            joined_at=datetime.now()
        )
        
        self.db.add(member)
        self.db.commit()
        return True
    
    def leave_organization(self, user_id: int, organization_id: int) -> bool:
        """用户离开组织"""
        member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.is_creator == False  # 创建者不能离开，只能解散
            )
        ).first()
        
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
    
    def remove_member(self, organization_id: int, user_id: int, remover_id: int) -> bool:
        """从组织中移除成员（只有创建者可以操作）"""
        # 检查操作者是否是创建者
        creator_member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == remover_id,
                OrganizationMember.is_creator == True
            )
        ).first()
        
        if not creator_member:
            return False  # 不是创建者，无权操作
        
        member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.is_creator == False  # 不能移除创建者
            )
        ).first()
        
        if member:
            self.db.delete(member)
            self.db.commit()
            return True
        return False
    
    def get_user_organizations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户加入的所有组织，包括创建的和加入的"""
        organizations = self.db.query(
            Organization,
            OrganizationMember.is_creator
        ).join(
            OrganizationMember,
            Organization.id == OrganizationMember.organization_id
        ).filter(
            OrganizationMember.user_id == user_id
        ).all()
        
        result = []
        for org, is_creator in organizations:
            # 获取成员数量
            member_count = self.db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == org.id
            ).count()
            
            result.append({
                "id": org.id,
                "name": org.name,
                "description": org.description,
                "invite_code": org.invite_code,
                "creator_id": org.creator_id,
                "created_at": org.created_at.isoformat(),
                "updated_at": org.updated_at.isoformat(),
                "is_creator": is_creator,
                "member_count": member_count
            })
        
        return result
    
    def get_organization_members(self, organization_id: int) -> List[Dict[str, Any]]:
        """获取组织的所有成员信息"""
        members = self.db.query(
            User,
            OrganizationMember.is_creator,
            OrganizationMember.joined_at
        ).join(
            OrganizationMember,
            User.id == OrganizationMember.user_id
        ).filter(
            OrganizationMember.organization_id == organization_id
        ).all()
        
        result = []
        for user, is_creator, joined_at in members:
            result.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "is_creator": is_creator,
                "joined_at": joined_at.isoformat() if hasattr(joined_at, 'isoformat') else str(joined_at)
            })
        
        return result
    
    def is_user_creator(self, user_id: int, organization_id: int) -> bool:
        """检查用户是否是组织的创建者"""
        member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.is_creator == True
            )
        ).first()
        return member is not None
    
    def is_user_member(self, user_id: int, organization_id: int) -> bool:
        """检查用户是否是组织的成员"""
        member = self.db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id
            )
        ).first()
        return member is not None

    def validate_user_exists(self, user_id: int) -> bool:
        """验证用户是否存在"""
        user = self.db.query(User).filter(User.id == user_id).first()
        return user is not None
    
    def _generate_unique_invite_code(self) -> str:
        """生成唯一的邀请码"""
        while True:
            # 生成8位大写字母数字组合
            code = str(uuid.uuid4()).replace('-', '').upper()[:8]
            
            # 检查是否已存在
            existing = self.db.query(Organization).filter(Organization.invite_code == code).first()
            if not existing:
                return code

# 获取数据库会话的辅助函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
