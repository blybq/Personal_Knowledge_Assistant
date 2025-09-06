from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
import time

from app.database.models import get_db, User
from app.User.user_service import UserService
from app.User.email_service import email_service

# 内存存储验证码（生产环境建议使用Redis）
verification_codes = {}

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Pydantic models for password reset
class SendResetCodeRequest(BaseModel):
    email: str

class VerifyResetCodeRequest(BaseModel):
    email: str
    verification_code: str

class ResetPasswordRequest(BaseModel):
    email: str
    verification_code: str
    new_password: str

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

def generate_verification_code(length: int = 6) -> str:
    """生成指定长度的数字验证码"""
    return ''.join(random.choices(string.digits, k=length))

def is_code_expired(timestamp: float, expiry_minutes: int = 10) -> bool:
    """检查验证码是否过期"""
    return time.time() > timestamp + (expiry_minutes * 60)

@router.post("/send-reset-code", response_model=ApiResponse)
async def send_reset_code(
    request: SendResetCodeRequest,
    db: Session = Depends(get_db)
):
    """发送密码重置验证码"""
    # 检查邮箱是否存在
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # 出于安全考虑，即使邮箱不存在也返回成功
        return ApiResponse(
            success=True,
            message="如果邮箱存在，验证码已发送"
        )
    
    # 生成6位数字验证码
    verification_code = generate_verification_code(6)
    
    # 存储验证码到内存（邮箱: (验证码, 时间戳)）
    verification_codes[request.email] = (verification_code, time.time())
    
    # 使用邮件服务发送验证码
    email_sent = email_service.send_verification_code(request.email, verification_code)
    
    if not email_sent:
        # 如果邮件发送失败，仍然返回成功（出于安全考虑）
        print(f"邮件发送失败，验证码为: {verification_code}")
    
    return ApiResponse(
        success=True,
        message="验证码已发送到您的邮箱"
    )

@router.post("/verify-reset-code", response_model=ApiResponse)
async def verify_reset_code(
    request: VerifyResetCodeRequest,
    db: Session = Depends(get_db)
):
    """验证密码重置验证码"""
    # 从内存中获取验证码
    if request.email not in verification_codes:
        return ApiResponse(
            success=False,
            message="验证码无效或已过期"
        )
    
    stored_code, timestamp = verification_codes[request.email]
    
    # 检查验证码是否匹配
    if stored_code != request.verification_code:
        return ApiResponse(
            success=False,
            message="验证码不正确"
        )
    
    # 检查验证码是否过期
    if is_code_expired(timestamp):
        # 删除过期的验证码
        del verification_codes[request.email]
        return ApiResponse(
            success=False,
            message="验证码已过期，请重新获取"
        )
    
    return ApiResponse(
        success=True,
        message="验证码验证成功"
    )

@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """重置用户密码"""
    # 验证验证码
    if request.email not in verification_codes:
        return ApiResponse(
            success=False,
            message="验证码无效或已过期"
        )
    
    stored_code, timestamp = verification_codes[request.email]
    
    # 检查验证码是否匹配
    if stored_code != request.verification_code:
        return ApiResponse(
            success=False,
            message="验证码不正确"
        )
    
    # 检查验证码是否过期
    if is_code_expired(timestamp):
        # 删除过期的验证码
        del verification_codes[request.email]
        return ApiResponse(
            success=False,
            message="验证码已过期，请重新获取"
        )
    
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # 删除验证码
        del verification_codes[request.email]
        return ApiResponse(
            success=False,
            message="用户不存在"
        )
    
    # 检查新密码是否与旧密码相同
    hashed_new_password = hashlib.sha256(request.new_password.encode('utf-8')).hexdigest()
    if user.hashed_password == hashed_new_password:
        # 删除验证码
        del verification_codes[request.email]
        return ApiResponse(
            success=False,
            message="新密码不能与旧密码相同"
        )
    
    # 更新用户密码
    user.hashed_password = hashed_new_password
    user.updated_at = datetime.now()
    
    # 删除已使用的验证码
    del verification_codes[request.email]
    
    db.commit()
    
    return ApiResponse(
        success=True,
        message="密码重置成功"
    )
