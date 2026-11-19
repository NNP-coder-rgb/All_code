"""
models/order.py — SQLAlchemy ORM Model cho Bảng Đơn Hàng (orders) & Chi Tiết Đơn Hàng (order_items)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Order(Base):
    """Bảng lưu trữ thông tin đơn đặt hàng."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="Mã đơn hàng số")
    order_code = Column(String(40), unique=True, index=True, nullable=False, comment="Mã định danh đơn (ORD-XXXX)")
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="Mã người mua")
    total_amount = Column(BigInteger, nullable=False, comment="Tổng tiền thanh toán cuối cùng (VNĐ)")
    shipping_fee = Column(BigInteger, default=0, nullable=False, comment="Phí vận chuyển")
    payment_method = Column(String(30), default="COD", nullable=False, comment="Phương thức thanh toán: COD, VNPay, Escrow")
    payment_status = Column(String(20), default="unpaid", nullable=False, comment="Trạng thái thanh toán: unpaid, paid, held_in_escrow")
    status = Column(String(30), default="pending", nullable=False, index=True, comment="Trạng thái đơn: pending, shipping, completed, cancelled")
    recipient_name = Column(String(100), nullable=False, comment="Tên người nhận hàng")
    recipient_phone = Column(String(20), nullable=False, comment="Số điện thoại người nhận")
    shipping_address = Column(Text, nullable=False, comment="Địa chỉ giao hàng chi tiết")
    note = Column(Text, nullable=True, comment="Ghi chú người mua gửi người bán")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Mối quan hệ ORM
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} code='{self.order_code}' total={self.total_amount}>"


class OrderItem(Base):
    """Bảng chi tiết các sản phẩm nằm trong từng đơn hàng."""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(255), nullable=False, comment="Lưu lại tên sản phẩm tại thời điểm mua")
    unit_price = Column(BigInteger, nullable=False, comment="Đơn giá sản phẩm tại thời điểm mua")
    quantity = Column(Integer, default=1, nullable=False, comment="Số lượng mua")
    subtotal = Column(BigInteger, nullable=False, comment="Thành tiền = đơn giá * số lượng")

    # Mối quan hệ ORM
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id} product='{self.product_name}'>"
