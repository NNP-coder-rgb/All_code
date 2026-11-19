"""
schemas/user.py — Pydantic Schemas Cho Đối Tượng Người Dùng (User)
Tách biệt hoàn toàn giữa dữ liệu đầu vào (Request validation) và đầu ra (Response serialization).
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    """Các trường thông tin cơ bản của User."""
    email: str = Field(..., description="Email người dùng (duy nhất)")
    phone: str = Field(..., description="Số điện thoại liên hệ (duy nhất)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên người dùng")
    role: str = Field(default="buyer", description="Vai trò: buyer, seller, admin")
    avatar_url: Optional[str] = Field(default=None, description="Đường dẫn ảnh đại diện")
    bio: Optional[str] = Field(default=None, description="Giới thiệu bản thân")


class UserCreate(UserBase):
    """Schema nhận request tạo mới người dùng (yêu cầu mật khẩu)."""
    password: str = Field(..., min_length=6, max_length=50, description="Mật khẩu khởi tạo tài khoản")


class UserUpdate(BaseModel):
    """Schema nhận request cập nhật thông tin người dùng (tất cả các trường đều là tùy chọn)."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=6, description="Mật khẩu mới nếu muốn đổi")


class UserResponse(UserBase):
    """Schema định dạng dữ liệu trả về cho Client (Ẩn password_hash bảo mật)."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Mã ID người dùng")
    is_active: bool = Field(..., description="Trạng thái tài khoản")
    created_at: datetime = Field(..., description="Ngày tạo tài khoản")
    updated_at: datetime = Field(..., description="Ngày cập nhật mới nhất")
