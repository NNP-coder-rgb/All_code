"""
auth_service.py — Nghiệp vụ Xác thực, eKYC và Quản lý Người dùng
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User, KYCVerification, UserAddress, BankAccount


class AuthService:
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def authenticate(db: Session, username_or_phone: str, password: str) -> Optional[User]:
        # Tìm theo phone, email hoặc username
        user = (
            db.query(User)
            .filter(
                (User.phone == username_or_phone)
                | (User.email == username_or_phone)
                | (User.username == username_or_phone)
            )
            .first()
        )
        if not user:
            return None
        # Kiểm tra mật khẩu (hỗ trợ cả hash đơn giản và plain text cho môi trường dev)
        if user.password_hash.startswith("pbkdf2:"):
            # Kiểm tra hậu tố hash đơn giản
            expected_pass = user.password_hash.split(":")[-1]
            if password == expected_pass or user.password_hash == password:
                return user
        elif user.password_hash == password:
            return user
        return None

    @staticmethod
    def register(db: Session, full_name: str, phone: str, password: str, role: str = "buyer", email: Optional[str] = None) -> User:
        user = User(
            full_name=full_name,
            phone=phone,
            email=email or f"{phone}@hybridstore.vn",
            password_hash=f"pbkdf2:sha256:{password}",
            role=role,
            membership_title="MEMBER",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
