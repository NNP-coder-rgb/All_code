"""
routers/auth_router.py — API Endpoints Xác Thực, Đăng Ký, Đăng Nhập & eKYC CCCD
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.common import BaseResponse
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    KYCVerificationCreate, KYCVerificationResponse
)
from services.auth_service import auth_service
from models.user import KYCVerification

router = APIRouter(prefix="/auth", tags=["Auth & Identity (Xác thực & Danh tính)"])


@router.post(
    "/register",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới"
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if auth_service.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_in.email}' đã được đăng ký"
        )
    if auth_service.get_by_phone(db, user_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Số điện thoại '{user_in.phone}' đã được đăng ký"
        )
    new_user = auth_service.create_user(db, user_in=user_in)
    return BaseResponse[UserResponse](
        success=True,
        message="Đăng ký tài khoản thành công",
        data=new_user
    )


@router.post(
    "/login",
    response_model=BaseResponse[dict],
    summary="Đăng nhập hệ thống"
)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, login_in.username_or_phone, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác"
        )
    # Trả về thông tin người dùng kèm token phiên làm việc
    user_data = UserResponse.model_validate(user).model_dump()
    return BaseResponse[dict](
        success=True,
        message="Đăng nhập thành công",
        data={
            "user": user_data,
            "access_token": f"bearer_{user.id}_token_session_2026",
            "token_type": "bearer"
        }
    )


@router.get(
    "/me",
    response_model=BaseResponse[UserResponse],
    summary="Lấy thông tin tài khoản hiện tại"
)
def get_current_user_profile(user_id: int = Query(..., description="ID tài khoản đăng nhập"), db: Session = Depends(get_db)):
    user = auth_service.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin tài khoản")
    return BaseResponse[UserResponse](
        success=True,
        message="Lấy hồ sơ cá nhân thành công",
        data=user
    )


@router.put(
    "/me",
    response_model=BaseResponse[UserResponse],
    summary="Cập nhật hồ sơ tài khoản hiện tại"
)
def update_current_user_profile(
    user_in: UserUpdate,
    user_id: int = Query(..., description="ID tài khoản đăng nhập"),
    db: Session = Depends(get_db)
):
    user = auth_service.update_user(db, user_id=user_id, user_in=user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản cần cập nhật")
    return BaseResponse[UserResponse](
        success=True,
        message="Cập nhật hồ sơ cá nhân thành công",
        data=user
    )


@router.post(
    "/ekyc",
    response_model=BaseResponse[KYCVerificationResponse],
    summary="Gửi hồ sơ định danh C06 eKYC (CCCD gắn chip)"
)
def submit_ekyc(
    kyc_in: KYCVerificationCreate,
    user_id: int = Query(..., description="ID tài khoản gửi hồ sơ eKYC"),
    db: Session = Depends(get_db)
):
    user = auth_service.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng")

    kyc = auth_service.submit_ekyc(db, user_id=user_id, kyc_in=kyc_in)
    return BaseResponse[KYCVerificationResponse](
        success=True,
        message="Đã gửi hồ sơ xác thực CCCD gắn chip thành công. Vui lòng chờ phê duyệt.",
        data=kyc
    )


@router.get(
    "/ekyc",
    response_model=BaseResponse[Optional[KYCVerificationResponse]],
    summary="Kiểm tra trạng thái định danh eKYC"
)
def get_ekyc_status(
    user_id: int = Query(..., description="ID tài khoản kiểm tra"),
    db: Session = Depends(get_db)
):
    kyc = db.query(KYCVerification).filter(KYCVerification.user_id == user_id).first()
    return BaseResponse[Optional[KYCVerificationResponse]](
        success=True,
        message="Lấy trạng thái định danh thành công" if kyc else "Người dùng chưa gửi hồ sơ eKYC",
        data=kyc
    )
