from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.models import get_db
from app.User.Login import SessionManager
from app.User.user_service import UserService
from app.User.admin_service import AdminService

router = APIRouter(prefix="/api", tags=["users"])

# Pydantic模型类
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateUsernameRequest(BaseModel):
    new_username: str
    current_password: str

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class DeleteSelfRequest(BaseModel):
    operated_user_id: Optional[int] = None
    current_user_id: Optional[int] = None

class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: dict = {"user": dict, "conversation": list}
    # user: dict = None
    # conversations: list = None

class DeleteResponse(BaseModel):
    success: bool
    message: str


@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    result = SessionManager.register_user(db, user.username, user.email, user.password)
    return RegisterResponse(**result)

@router.post("/login", response_model=LoginResponse)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    result = SessionManager.login(db, user_login.email, user_login.password)
    return result

@router.put("/users/{user_id}/username", response_model=RegisterResponse)
def update_username(user_id: int, request: UpdateUsernameRequest, db: Session = Depends(get_db)):
    """修改用户名"""
    # 验证当前密码
    user = SessionManager.authenticate_user(db, user_id=user_id, password=request.current_password)
    if not user:
        raise HTTPException(status_code=401, detail="当前密码错误")
    
    # 更新用户名
    result = UserService.update_username(db, user_id, request.new_username)
    return RegisterResponse(**result)

@router.put("/users/{user_id}/password", response_model=RegisterResponse)
def update_password(user_id: int, request: UpdatePasswordRequest, db: Session = Depends(get_db)):
    """修改密码"""
    # 验证当前密码
    user = SessionManager.authenticate_user(db, user_id=user_id, password=request.current_password)
    if not user:
        raise HTTPException(status_code=401, detail="当前密码错误")
    
    # 更新密码
    result = UserService.update_password(db, user_id, request.new_password)
    return RegisterResponse(**result)

@router.delete("/users/self-delete", response_model=DeleteResponse)
async def self_delete_account(
    operated_user_id: int,
    current_user_id: int,
    db: Session = Depends(get_db)
):
    """用户自己注销账号"""
    try:
        # 这里需要从会话中获取当前用户ID
        # 在实际实现中，应该从JWT token或会话中获取用户ID
        # 这里只是一个示例，需要根据实际认证系统调整
        # current_user_id = 1  # 示例值，需要替换为实际的用户ID获取逻辑

        if (operated_user_id != current_user_id):
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"非本人或管理员注销: {str(e)}"
        )
        
        success = AdminService.delete_user_account(db, current_user_id)
        if success:
            return {
                "success": True,
                "message": "账号注销成功"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号注销失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"账号注销失败: {str(e)}"
        )

