"""
models/user.py — SQLAlchemy ORM Model cho Bảng Người Dùng (users)
Bao gồm đầy đủ kiểu dữ liệu, khóa chính, ràng buộc unique, khóa ngoại, created_at và updated_at.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class User(Base):
    """Bảng lưu trữ thông tin người dùng và tài khoản hệ thống."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="Khóa chính tự tăng")
    email = Column(String(120), unique=True, index=True, nullable=False, comment="Email đăng nhập duy nhất")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="Số điện thoại định danh")
    password_hash = Column(String(255), nullable=False, comment="Mật khẩu đã được mã hóa")
    full_name = Column(String(100), nullable=False, comment="Họ và tên đầy đủ")
    role = Column(String(20), default="buyer", nullable=False, comment="Vai trò: buyer, seller, admin")
    avatar_url = Column(Text, nullable=True, comment="Đường dẫn ảnh đại diện")
    bio = Column(Text, nullable=True, comment="Tiểu sử / Giới thiệu bản thân")
    is_active = Column(Boolean, default=True, nullable=False, comment="Trạng thái tài khoản hoạt động")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="Thời điểm tạo bản ghi")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="Thời điểm cập nhật mới nhất")

    # Mối quan hệ ORM (Relationships)
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="buyer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"
