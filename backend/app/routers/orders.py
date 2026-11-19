"""
orders.py — Router xử lý Đơn hàng & Tra cứu vận đơn
"""

from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.order import Order, OrderParcel, OrderItem, OrderTrackingEvent


def handle_get_orders(db: Session, user_id: str) -> Dict[str, Any]:
    orders = (
        db.query(Order)
        .filter(Order.buyer_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return {
        "success": True,
        "message": "Lấy danh sách đơn hàng thành công",
        "data": [o.to_dict() for o in orders],
        "status_code": 200
    }


def handle_get_order_detail(db: Session, order_identifier: str) -> Dict[str, Any]:
    order = (
        db.query(Order)
        .filter((Order.id == order_identifier) | (Order.order_code == order_identifier))
        .first()
    )
    if not order:
        return {"success": False, "message": "Không tìm thấy đơn hàng", "status_code": 404}
    return {
        "success": True,
        "message": "Lấy chi tiết đơn hàng thành công",
        "data": order.to_dict(),
        "status_code": 200
    }
