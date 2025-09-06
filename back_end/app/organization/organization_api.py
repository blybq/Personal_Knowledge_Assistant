from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

from app.database.models import get_db, OrganizationMember, User
from app.organization.organization_service import OrganizationService

router = APIRouter(prefix="/api/organizations", tags=["organizations"])

# Pydantic models for request/response
class OrganizationCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: int  # 前端传递的用户ID

class OrganizationUpdateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: int  # 前端传递的用户ID

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    invite_code: str
    creator_id: int
    created_at: str
    updated_at: str
    is_creator: bool
    member_count: int

    class Config:
        from_attributes = True

class OrganizationMemberResponse(BaseModel):
    user_id: int
    username: str
    email: str
    is_creator: bool
    joined_at: str

class JoinOrganizationRequest(BaseModel):
    invite_code: str
    user_id: int  # 前端传递的用户ID

class DeleteOrganizationRequest(BaseModel):
    user_id: int  # 前端传递的用户ID

class LeaveOrganizationRequest(BaseModel):
    user_id: int  # 前端传递的用户ID

class GetMembersRequest(BaseModel):
    user_id: int  # 前端传递的用户ID

class RemoveMemberRequest(BaseModel):
    user_id: int  # 前端传递的用户ID（操作者的用户ID）

class ApiResponseList(BaseModel):
    success: bool
    data: List = None

class ApiResponseDict(BaseModel):
    success: bool
    data: dict = None

# 定义泛型类型 T
T = TypeVar("T")

# 泛型 ApiResponse
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

@router.get("/user/{user_id}", response_model=ApiResponse[List[OrganizationResponse]])
async def get_user_organizations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户的所有组织（创建的和加入的）"""
    service = OrganizationService(db)
    organizations = service.get_user_organizations(user_id)
    # return organizations
    return {
        "success": True,
        "data": organizations
    }

@router.post("/", response_model=ApiResponse[OrganizationResponse])
async def create_organization(
    request: OrganizationCreateRequest,
    db: Session = Depends(get_db)
):
    """创建新的组织"""
    service = OrganizationService(db)
    
    # 验证用户是否存在
    if not service.validate_user_exists(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    organization = service.create_organization(
        name=request.name,
        description=request.description,
        creator_id=request.user_id
    )
    
    # 返回包含创建者信息和成员数量的响应
    return {
        "success": True,
        "data": {
            "id": organization.id,
            "name": organization.name,
            "description": organization.description,
            "invite_code": organization.invite_code,
            "creator_id": organization.creator_id,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat(),
            "is_creator": True,
            "member_count": 1  # 创建时只有创建者一个成员
        }
    }

@router.put("/{organization_id}", response_model=ApiResponse[OrganizationResponse])
async def update_organization(
    organization_id: int,
    request: OrganizationUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新组织信息（只有创建者可以操作）"""
    service = OrganizationService(db)
    
    # 检查用户是否是创建者
    if not service.is_user_creator(request.user_id, organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有创建者可以修改组织信息"
        )
    
    organization = service.update_organization(
        organization_id=organization_id,
        name=request.name,
        description=request.description
    )
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    # 获取更新后的组织信息
    user_orgs = service.get_user_organizations(request.user_id)
    updated_org = next((org for org in user_orgs if org["id"] == organization_id), None)
    
    if not updated_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    return updated_org

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: int,
    request: DeleteOrganizationRequest,
    db: Session = Depends(get_db)
):
    """删除组织（只有创建者可以操作）"""
    service = OrganizationService(db)
    
    # 检查用户是否是创建者
    if not service.is_user_creator(request.user_id, organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有创建者可以删除组织"
        )
    
    success = service.delete_organization(organization_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="组织不存在"
        )
    
    return {"success": True, "message": "组织删除成功"}

@router.get("/search")
async def search_organization(
    invite_code: str,
    db: Session = Depends(get_db)
):
    """通过邀请码搜索组织"""
    service = OrganizationService(db)
    organization = service.get_organization_by_invite_code(invite_code)
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应的组织"
        )
    
    # 获取成员数量
    member_count = service.db.query(OrganizationMember)\
        .filter(OrganizationMember.organization_id == organization.id)\
        .count()
    
    return {
            "success": True,
            "data":{
            "id": organization.id,
            "name": organization.name,
            "description": organization.description,
            "invite_code": organization.invite_code,
            "creator_id": organization.creator_id,
            "created_at": organization.created_at.isoformat(),
            "updated_at": organization.updated_at.isoformat(),
            "member_count": member_count
        }
    }

@router.post("/join")
async def join_organization(
    request: JoinOrganizationRequest,
    db: Session = Depends(get_db)
):
    """加入组织"""
    service = OrganizationService(db)
    
    # 验证用户是否存在
    if not service.validate_user_exists(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 通过邀请码获取组织
    organization = service.get_organization_by_invite_code(request.invite_code)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码无效"
        )
    
    # 加入组织
    success = service.join_organization(request.user_id, organization.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经加入该组织或加入失败"
        )
    
    return {"success": True, "message": "成功加入组织"}

@router.post("/{organization_id}/leave")
async def leave_organization(
    organization_id: int,
    request: LeaveOrganizationRequest,
    db: Session = Depends(get_db)
):
    """离开组织"""
    service = OrganizationService(db)
    
    # 验证用户是否存在
    if not service.validate_user_exists(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否是创建者（创建者不能离开，只能解散）
    if service.is_user_creator(request.user_id, organization_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="创建者不能离开组织，请解散组织"
        )
    
    success = service.leave_organization(request.user_id, organization_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未加入该组织或离开失败"
        )
    
    return {"success": True, "message": "成功离开组织"}

@router.post("/{organization_id}/members", response_model=ApiResponse[List[OrganizationMemberResponse]])
async def get_organization_members(
    organization_id: int,
    request: GetMembersRequest,
    db: Session = Depends(get_db)
):
    """获取组织成员列表"""
    service = OrganizationService(db)
    
    # 验证用户是否存在
    if not service.validate_user_exists(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户是否是组织成员
    if not service.is_user_member(request.user_id, organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该组织信息"
        )
    
    members = service.get_organization_members(organization_id)
    return {
        "success": True,
        "data": members
    }

@router.post("/{organization_id}/members/{user_id}/remove")
async def remove_organization_member(
    organization_id: int,
    user_id: int,
    request: RemoveMemberRequest,
    db: Session = Depends(get_db)
):
    """从组织中移除成员（只有创建者可以操作）"""
    service = OrganizationService(db)
    
    # 验证用户是否存在
    if not service.validate_user_exists(request.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    success = service.remove_member(organization_id, user_id, request.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作或成员不存在"
        )
    
    return {"success": True, "message": "成员移除成功"}
