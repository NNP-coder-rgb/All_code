"""
services/order_service.py — Lớp Xử Lý Nghiệp Vụ Cho Đơn Hàng & Tách Kiện
"""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from models.order import Order, OrderItem
from schemas.order import OrderCreate, OrderUpdate


class OrderService:
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def get_by_code(db: Session, order_code: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_code == order_code).first()

    @staticmethod
    def get_orders(
        db: Session,
        buyer_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Order], int]:
        query = db.query(Order)

        if buyer_id:
            query = query.filter(Order.buyer_id == buyer_id)

        if status:
            query = query.filter(Order.status == status)

        total = query.count()
        orders = query.order_by(Order.id.desc()).offset(skip).limit(limit).all()
        return orders, total

    @staticmethod
    def create_order(db: Session, buyer_id: int, order_in: OrderCreate) -> Order:
        order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Tính tổng tiền từ các items
        items_total = sum(item.unit_price * item.quantity for item in order_in.items)
        final_total = items_total + order_in.shipping_fee

        db_order = Order(
            order_code=order_code,
            buyer_id=buyer_id,
            total_amount=final_total,
            shipping_fee=order_in.shipping_fee,
            payment_method=order_in.payment_method,
            payment_status="unpaid",
            status="pending",
            recipient_name=order_in.recipient_name,
            recipient_phone=order_in.recipient_phone,
            shipping_address=order_in.shipping_address,
            note=order_in.note
        )
        db.add(db_order)
        db.flush()

        # Tạo Order Items
        for it in order_in.items:
            db_item = OrderItem(
                order_id=db_order.id,
                product_id=it.product_id,
                product_name=it.product_name,
                unit_price=it.unit_price,
                quantity=it.quantity,
                subtotal=it.unit_price * it.quantity
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def update_order(db: Session, order_id: int, order_in: OrderUpdate) -> Optional[Order]:
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None

        for key, value in order_in.model_dump(exclude_unset=True).items():
            setattr(db_order, key, value)

        db.commit()
        db.refresh(db_order)
        return db_order


order_service = OrderService()
