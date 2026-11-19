"""
user.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Module Người dùng & Định danh eKYC
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    phone_number: str = Field(..., description="Số điện thoại đăng nhập")
    full_name: str = Field(..., description="Họ và tên người dùng")
    email: Optional[str] = Field(default=None, description="Địa chỉ email")
    role: str = Field(default="buyer", description="Vai trò: buyer, seller, admin, inspector")


class UserLoginRequest(BaseModel):
    username_or_phone: str = Field(..., description="Số điện thoại hoặc Email")
    password: str = Field(..., description="Mật khẩu người dùng")


class UserRegisterRequest(UserBase):
    password: str = Field(..., min_length=6, description="Mật khẩu khởi tạo")


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    shop_name: Optional[str] = None
    shop_description: Optional[str] = None


class UserResponse(BaseModel):
    """Schema chuẩn trả về thông tin User."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str
    full_name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    kyc_status: str
    shop_name: Optional[str] = None
    shop_rating: float = 5.0
    shop_description: Optional[str] = None
    is_active: bool = True
    loyalty_points: int = 0
    vip_tier: str = "Standard"
    created_at: Optional[datetime] = None


class UserAddressBase(BaseModel):
    recipient_name: str
    phone_number: str
    province_city: str
    district: str
    ward: str
    street_address: str
    is_default: bool = False
    address_type: str = "home"


class UserAddressCreateRequest(UserAddressBase):
    pass


class UserAddressResponse(UserAddressBase):
    """Schema chuẩn trả về địa chỉ giao hàng."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: Optional[datetime] = None


class KYCVerificationRequest(BaseModel):
    id_card_number: str = Field(..., description="Số CCCD 12 số")
    full_name: str = Field(..., description="Họ tên in hoa trên CCCD")
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    place_of_origin: Optional[str] = None
    place_of_residence: Optional[str] = None
    card_front_url: str = Field(..., description="Link ảnh mặt trước CCCD")
    card_back_url: str = Field(..., description="Link ảnh mặt sau CCCD")
    face_selfie_url: str = Field(..., description="Link ảnh chân dung / Video liveness")


class KYCVerificationResponse(BaseModel):
    """Schema chuẩn trả về kết quả định danh eKYC."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    id_card_number: str
    full_name: str
    status: str
    rejection_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class BankAccountRequest(BaseModel):
    bank_code: str = Field(..., description="Mã ngân hàng (VCB, TCB, MB, ...)")
    bank_name: str = Field(..., description="Tên ngân hàng")
    account_number: str = Field(..., description="Số tài khoản ngân hàng")
    account_holder: str = Field(..., description="Tên chủ tài khoản không dấu")
    is_default: bool = False


class BankAccountResponse(BankAccountRequest):
    """Schema chuẩn trả về thông tin tài khoản ngân hàng."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_verified: bool = True
    created_at: Optional[datetime] = None
