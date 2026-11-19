"""
disputes.py — Router xử lý Phòng Trọng Tài Khiếu Nại 3 Bên
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.dispute import Dispute, DisputeEvidence, DisputeMessage


def handle_get_disputes(db: Session, user_id: str) -> Dict[str, Any]:
    disputes = (
        db.query(Dispute)
        .filter((Dispute.buyer_id == user_id) | (Dispute.seller_id == user_id) | (Dispute.arbitrator_admin_id == user_id))
        .order_by(Dispute.created_at.desc())
        .all()
    )
    return {
        "success": True,
        "message": "Lấy danh sách khiếu nại thành công",
        "data": [d.to_dict() for d in disputes],
        "status_code": 200
    }


def handle_get_dispute_detail(db: Session, dispute_identifier: str) -> Dict[str, Any]:
    dispute = (
        db.query(Dispute)
        .filter((Dispute.id == dispute_identifier) | (Dispute.dispute_code == dispute_identifier))
        .first()
    )
    if not dispute:
        return {"success": False, "message": "Không tìm thấy vụ việc khiếu nại", "status_code": 404}
    return {
        "success": True,
        "message": "Lấy chi tiết phòng trọng tài thành công",
        "data": dispute.to_dict(),
        "status_code": 200
    }
