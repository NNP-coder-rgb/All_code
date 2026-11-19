"""
vouchers.py — Router xử lý Khuyến mãi & Voucher
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.voucher import Voucher


def handle_get_vouchers(db: Session) -> Dict[str, Any]:
    vouchers = db.query(Voucher).filter(Voucher.is_active == True).all()
    return {
        "success": True,
        "message": "Lấy danh sách voucher thành công",
        "data": [v.to_dict() for v in vouchers],
        "status_code": 200
    }
