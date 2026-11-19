"""
auth.py — Router xử lý Đăng nhập, Đăng ký, eKYC và Hồ sơ Người dùng
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User, KYCVerification
from app.services.auth_service import auth_service


def handle_login(db: Session, body: Dict[str, Any]) -> Dict[str, Any]:
    username = body.get("username_or_phone") or body.get("username") or body.get("phone", "")
    password = body.get("password", "")
    if not username or not password:
        return {"success": False, "message": "Vui lòng nhập tài khoản và mật khẩu", "status_code": 400}
    user = auth_service.authenticate(db, username, password)
    if not user:
        return {"success": False, "message": "Số điện thoại hoặc mật khẩu không chính xác", "status_code": 401}
    return {
        "success": True,
        "message": f"Đăng nhập thành công! Chào mừng {user.full_name}",
        "data": {
            "token": f"token-{user.id}-session",
            "user": user.to_dict()
        },
        "status_code": 200
    }


def handle_register(db: Session, body: Dict[str, Any]) -> Dict[str, Any]:
    phone = body.get("phone_number") or body.get("phone", "")
    full_name = body.get("full_name", "")
    password = body.get("password", "")
    role = body.get("role", "buyer")
    if not phone or not full_name or not password:
        return {"success": False, "message": "Vui lòng nhập đầy đủ họ tên, số điện thoại và mật khẩu", "status_code": 400}
    if auth_service.get_by_phone(db, phone):
        return {"success": False, "message": "Số điện thoại này đã được đăng ký tài khoản", "status_code": 409}
    user = auth_service.register(db, full_name, phone, password, role)
    return {
        "success": True,
        "message": "Đăng ký tài khoản thành công!",
        "data": user.to_dict(),
        "status_code": 201
    }


def handle_profile(db: Session, user_id: str) -> Dict[str, Any]:
    user = auth_service.get_by_id(db, user_id)
    if not user:
        return {"success": False, "message": "Không tìm thấy người dùng", "status_code": 404}
    res = user.to_dict()
    if user.kyc:
        res["kyc"] = user.kyc.to_dict()
    if user.addresses:
        res["addresses"] = [a.to_dict() for a in user.addresses]
    if user.bank_accounts:
        res["bankAccounts"] = [b.to_dict() for b in user.bank_accounts]
    return {"success": True, "message": "Lấy thông tin thành công", "data": res, "status_code": 200}
