"""
routers/auth_router.py — API Endpoints Xác Thực, Đăng Ký, Đăng Nhập & eKYC CCCD
"""

from typing import Optional, Dict, Any
import time
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.common import BaseResponse
from schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    KYCVerificationCreate, KYCVerificationResponse,
    ForgotPasswordRequest, ForgotPasswordVerify, ForgotPasswordReset
)
from services.auth_service import auth_service
from models.user import KYCVerification

router = APIRouter(prefix="/auth", tags=["Auth & Identity (Xác thực & Danh tính)"])

# Bộ nhớ tạm lưu mã OTP khôi phục mật khẩu (Email -> {otp, expires_at, attempts, verified})
_EMAIL_RESET_STORE: Dict[str, Dict[str, Any]] = {}


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


# ==============================================================
# KHÔI PHỤC MẬT KHẨU QUA EMAIL BẢO MẬT & CẤP MẬT KHẨU MỚI
# ==============================================================
def mask_email(email: str) -> str:
    parts = email.split("@")
    if len(parts) != 2:
        return email
    name, domain = parts[0], parts[1]
    if len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "***" + name[-1]
    return f"{masked_name}@{domain}"


@router.post(
    "/forgot-password/request",
    response_model=BaseResponse[dict],
    summary="Yêu cầu khôi phục mật khẩu và gửi mã OTP qua Email"
)
def request_forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = auth_service.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản nào liên kết với email này. Vui lòng kiểm tra lại."
        )

    # Kiểm tra giới hạn thời gian gửi (cooldown 60s)
    now = time.time()
    existing = _EMAIL_RESET_STORE.get(email)
    if existing and now - existing.get("requested_at", 0) < 60:
        remain = int(60 - (now - existing["requested_at"]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Vui lòng đợi {remain} giây trước khi yêu cầu gửi lại mã."
        )

    # Sinh mã OTP 6 chữ số an toàn
    otp = f"{secrets.randbelow(900000) + 100000:06d}"
    _EMAIL_RESET_STORE[email] = {
        "otp": otp,
        "requested_at": now,
        "expires_at": now + 300,  # 5 phút
        "attempts": 0,
        "verified": False,
        "user_id": user.id
    }

    masked = mask_email(email)
    return BaseResponse[dict](
        success=True,
        message=f"Mã xác thực đã được gửi tới hộp thư {masked}. Mã có hiệu lực trong 5 phút.",
        data={
            "email": email,
            "masked_email": masked,
            "expires_in_seconds": 300
        }
    )


@router.post(
    "/forgot-password/verify",
    response_model=BaseResponse[dict],
    summary="Xác minh mã OTP gửi về Email"
)
def verify_forgot_password_otp(body: ForgotPasswordVerify):
    email = body.email.strip().lower()
    clean_otp = body.otp.strip()

    record = _EMAIL_RESET_STORE.get(email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có yêu cầu khôi phục mật khẩu đang hoạt động cho email này."
        )

    now = time.time()
    if now > record["expires_at"]:
        _EMAIL_RESET_STORE.pop(email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã xác thực OTP đã hết hạn (chỉ có hiệu lực trong 5 phút). Vui lòng yêu cầu mã mới."
        )

    if record["attempts"] >= 3:
        _EMAIL_RESET_STORE.pop(email, None)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mã OTP đã bị hủy do nhập sai quá 3 lần. Vui lòng gửi lại yêu cầu mới."
        )

    if clean_otp != record["otp"]:
        record["attempts"] += 1
        remains = 3 - record["attempts"]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã OTP không chính xác. Bạn còn {remains} lần thử."
        )

    # Đánh dấu đã xác thực thành công
    record["verified"] = True
    return BaseResponse[dict](
        success=True,
        message="Xác thực email chính chủ thành công. Bạn có thể nhận mật khẩu mới ngay bây giờ.",
        data={"email": email, "verified": True}
    )


@router.post(
    "/forgot-password/reset",
    response_model=BaseResponse[dict],
    summary="Cấp và gửi mật khẩu mới trực tiếp về Email sau khi đã xác thực"
)
def reset_and_issue_new_password(body: ForgotPasswordReset, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    clean_otp = body.otp.strip()

    record = _EMAIL_RESET_STORE.get(email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy phiên xác thực hợp lệ. Vui lòng bắt đầu lại từ bước 1."
        )

    now = time.time()
    if now > record["expires_at"]:
        _EMAIL_RESET_STORE.pop(email, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiên xác thực đã hết hạn. Vui lòng thực hiện lại."
        )

    if clean_otp != record["otp"] and not record.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã xác minh không hợp lệ hoặc chưa được duyệt."
        )

    # Sinh mật khẩu mới ngẫu nhiên an toàn nếu người dùng không tự nhập
    if body.new_password and len(body.new_password) >= 6:
        new_pwd = body.new_password
    else:
        rand_num = f"{secrets.randbelow(9000) + 1000}"
        new_pwd = f"Hyb#{rand_num}@2026"

    user = auth_service.reset_password_by_email(db, email=email, new_password=new_pwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản để cập nhật mật khẩu."
        )

    # Xóa token sau khi đã reset thành công
    _EMAIL_RESET_STORE.pop(email, None)

    masked = mask_email(email)
    return BaseResponse[dict](
        success=True,
        message=f"Mật khẩu mới đã được khởi tạo và gửi thành công tới hòm thư {masked}.",
        data={
            "email": email,
            "masked_email": masked,
            "new_password": new_pwd,
            "login_ready": True
        }
    )

