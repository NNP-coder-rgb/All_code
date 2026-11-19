"""
models/user.py — Models SQLAlchemy cho Phân hệ Người Dùng, Định Danh eKYC CCCD, Sổ Địa Chỉ & Ngân Hàng
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Bảng 1: users — Người dùng và tài khoản hệ thống (Buyer, Seller, Admin, Inspector)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    username = Column(String(60), unique=True, nullable=True)
    role = Column(String(20), default="buyer", nullable=False)  # 'buyer', 'seller', 'admin', 'inspector'
    avatar_url = Column(Text, default="")
    membership_title = Column(String(50), default="VIP BUYER")
    bio = Column(Text, default="")
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    vip_points = Column(Integer, default=1500, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Quan hệ ORM
    kyc = relationship("KYCVerification", foreign_keys="[KYCVerification.user_id]", back_populates="user", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    wallet = relationship("EscrowWallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    products = relationship("Product", back_populates="seller")
    orders = relationship("Order", back_populates="buyer")
    reviews = relationship("ProductReview", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self, include_sensitive: bool = False):
        data = {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "fullName": self.full_name,
            "full_name": self.full_name,
            "username": self.username,
            "role": self.role,
            "avatar": self.avatar_url,
            "avatar_url": self.avatar_url,
            "membershipTitle": self.membership_title,
            "bio": self.bio,
            "vipPoints": self.vip_points,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data


class KYCVerification(Base):
    """Bảng 2: kyc_verifications — Hồ sơ xác thực Căn cước công dân gắn chip (eKYC L2)."""
    __tablename__ = "kyc_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    id_card_number = Column(String(12), unique=True, nullable=False)
    full_name_on_card = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=True)  # 'Nam', 'Nữ', 'Khác'
    permanent_address = Column(Text, nullable=False)
    front_image_url = Column(Text, nullable=False)
    back_image_url = Column(Text, nullable=False)
    selfie_image_url = Column(Text, default="")
    status = Column(String(20), default="pending", nullable=False)  # 'unverified', 'pending', 'approved', 'rejected'
    rejection_reason = Column(Text, default="")
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id], back_populates="kyc")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "idCardNumber": self.id_card_number,
            "fullNameOnCard": self.full_name_on_card,
            "dateOfBirth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "permanentAddress": self.permanent_address,
            "frontImageUrl": self.front_image_url,
            "backImageUrl": self.back_image_url,
            "selfieImageUrl": self.selfie_image_url,
            "status": self.status,
            "rejectionReason": self.rejection_reason,
            "reviewedAt": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class UserAddress(Base):
    """Bảng 3: user_addresses — Sổ địa chỉ giao nhận hàng đa cấp."""
    __tablename__ = "user_addresses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    province = Column(String(60), nullable=False)
    district = Column(String(60), nullable=False)
    ward = Column(String(60), nullable=False)
    street_address = Column(Text, nullable=False)
    full_address = Column(Text, nullable=False)
    address_type = Column(String(20), default="home")  # 'home', 'office'
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="addresses")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "recipientName": self.recipient_name,
            "phone": self.phone,
            "province": self.province,
            "district": self.district,
            "ward": self.ward,
            "streetAddress": self.street_address,
            "fullAddress": self.full_address,
            "addressType": self.address_type,
            "isDefault": self.is_default,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class BankAccount(Base):
    """Bảng 4: bank_accounts — Tài khoản ngân hàng liên kết Napas 24/7."""
    __tablename__ = "bank_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_code = Column(String(20), nullable=False)  # VCB, TCB, MB, VPB...
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(30), nullable=False)
    account_holder = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="bank_accounts")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "bankCode": self.bank_code,
            "bankName": self.bank_name,
            "accountNumber": self.account_number,
            "accountHolder": self.account_holder,
            "isDefault": self.is_default,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
