from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.database.models import get_db
from app.User.admin_service import AdminService
from app.User.Login import SessionManager

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Pydantic模型类
class UserBanRequest(BaseModel):
    operated_user_id: Optional[int] = None
    reason: Optional[str] = None

class OrganizationDeleteRequest(BaseModel):
    org_id: Optional[int] = None
    reason: Optional[str] = None

class UserDeleteRequest(BaseModel):
    operated_user_id: Optional[int] = None
    reason: Optional[str] = None

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

class AdminResponseDict(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class AdminResponseList(BaseModel):
    success: bool
    message: str
    data: Optional[list] = None

# 管理员权限验证依赖
async def verify_admin(user_id: int, db: Session = Depends(get_db)):
    """验证用户是否为管理员"""
    if not AdminService.is_admin(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user_id

@router.get("/users", response_model=AdminResponseDict)
async def get_all_users(
    page: int = 1,
    page_size: int = 20,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取所有用户列表（管理员权限）"""
    try:
        result = AdminService.get_all_users(db, page, page_size)
        return {
            "success": True,
            "message": "获取用户列表成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )

@router.get("/organizations", response_model=AdminResponseDict)
async def get_all_organizations(
    page: int = 1,
    page_size: int = 20,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取所有组织列表（管理员权限）"""
    try:
        result = AdminService.get_all_organizations(db, page, page_size)
        return {
            "success": True,
            "message": "获取组织列表成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取组织列表失败: {str(e)}"
        )

@router.post("/users/{user_id}/ban", response_model=AdminResponseList)
async def ban_user(
    user_id: int,
    ban_request: UserBanRequest,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """封禁用户（管理员权限）"""
    try:
        success = AdminService.ban_user(db, current_user_id, ban_request.operated_user_id, ban_request.reason)
        if success:
            return AdminResponseList(
                success=True,
                message=f"用户封禁成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户封禁失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户封禁失败: {str(e)}"
        )

@router.post("/users/{user_id}/unban", response_model=AdminResponseList)
async def unban_user(
    user_id: int,
    ban_request: UserBanRequest,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """解封用户（管理员权限）"""
    try:
        success = AdminService.unban_user(db, current_user_id, ban_request.operated_user_id, ban_request.reason)
        if success:
            return AdminResponseList(
                success=True,
                message=f"用户解封成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户解封失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户解封失败: {str(e)}"
        )

@router.delete("/organizations/{user_id}", response_model=AdminResponseList)
async def delete_organization(
    user_id: int,
    delete_request: OrganizationDeleteRequest,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """解散组织（管理员权限）"""
    try:
        success = AdminService.delete_organization(db, current_user_id, delete_request.org_id, delete_request.reason)
        if success:
            return AdminResponseList(
                success=True,
                message=f"组织解散成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="组织解散失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"组织解散失败: {str(e)}"
        )

@router.get("/users/{operated_user_id}/details", response_model=AdminResponseDict)
async def get_user_details(
    operated_user_id: int,
    user_id: int,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取用户详细信息（管理员权限）"""
    try:
        user_details = AdminService.get_user_details(db, operated_user_id)
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return {
            "success": True,
            "message": "获取用户详情成功",
            "data": user_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )

@router.get("/organizations/{organization_id}/details", response_model=AdminResponseDict)
async def get_organization_details(
    organization_id: int,
    user_id: int,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取组织详细信息（管理员权限）"""
    try:
        org_details = AdminService.get_organization_details(db, organization_id)
        if not org_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="组织不存在"
            )
        
        return {
            "success": True,
            "message": "获取组织详情成功",
            "data": org_details
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取组织详情失败: {str(e)}"
        )

@router.delete("/users/{user_id}", response_model=AdminResponseList)
async def delete_user_account(
    user_id: int,
    delete_request: UserDeleteRequest,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """删除用户账号（管理员权限）"""
    try:
        success = AdminService.delete_user_account(db, delete_request.operated_user_id, current_user_id, delete_request.reason)
        if success:
            return AdminResponseList(
                success=True,
                message="用户账号删除成功"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账号删除失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"用户账号删除失败: {str(e)}"
        )

@router.get("/operations", response_model=AdminResponseDict)
async def get_admin_operations(
    page: int = 1,
    page_size: int = 20,
    current_user_id: int = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """获取管理员操作日志（管理员权限）"""
    try:
        result = AdminService.get_admin_operations(db, page, page_size)
        return {
            "success": True,
            "message": "获取操作日志成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取操作日志失败: {str(e)}"
        )

