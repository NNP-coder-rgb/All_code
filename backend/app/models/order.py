"""
models/order.py — Models SQLAlchemy cho Đơn Hàng, Phân Tách Kiện Hàng Multi-Vendor & Vận Đơn
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Order(Base):
    """Bảng 12: orders — Hóa đơn mua sắm trung tâm & Xuất VAT."""
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: f"ord-{uuid.uuid4().hex[:8]}")
    order_code = Column(String(30), unique=True, index=True, nullable=False)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    subtotal = Column(BigInteger, nullable=False)
    shipping_fee = Column(BigInteger, default=0, nullable=False)
    discount_amount = Column(BigInteger, default=0, nullable=False)
    total_amount = Column(BigInteger, nullable=False)
    voucher_id = Column(String(36), ForeignKey("vouchers.id", ondelete="SET NULL"), nullable=True)
    payment_method = Column(String(20), nullable=False)  # 'COD', 'VIETQR', 'CARD', 'NAPAS_ESCROW'
    payment_status = Column(String(20), default="unpaid", nullable=False)  # 'unpaid', 'paid', 'refunded', 'held_in_escrow'
    shipping_method = Column(String(30), default="standard", nullable=False)  # 'standard', 'express_2h'
    recipient_name = Column(String(100), nullable=False)
    recipient_phone = Column(String(15), nullable=False)
    shipping_address = Column(Text, nullable=False)
    buyer_note = Column(Text, default="")
    vat_requested = Column(Boolean, default=False, nullable=False)
    vat_company_name = Column(String(150), default="")
    vat_tax_code = Column(String(30), default="")
    vat_company_address = Column(Text, default="")
    status = Column(String(20), default="pending", nullable=False, index=True)  # 'pending', 'confirmed', 'shipping', 'delivered', 'completed', 'cancelled', 'disputed'
    step_index = Column(Integer, default=1, nullable=False)  # 1: Đặt đơn, 2: Bàn giao, 3: Đang phát, 4: Đã nhận
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    buyer = relationship("User", back_populates="orders")
    voucher = relationship("Voucher", back_populates="orders")
    parcels = relationship("OrderParcel", back_populates="order", cascade="all, delete-orphan")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    dispute = relationship("Dispute", back_populates="order", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "orderCode": self.order_code,
            "buyerId": self.buyer_id,
            "buyerName": self.buyer.full_name if self.buyer else None,
            "subtotal": self.subtotal,
            "shippingFee": self.shipping_fee,
            "discountAmount": self.discount_amount,
            "totalAmount": self.total_amount,
            "paymentMethod": self.payment_method,
            "paymentStatus": self.payment_status,
            "shippingMethod": self.shipping_method,
            "recipientName": self.recipient_name,
            "recipientPhone": self.recipient_phone,
            "shippingAddress": self.shipping_address,
            "buyerNote": self.buyer_note,
            "vatRequested": self.vat_requested,
            "vatCompanyName": self.vat_company_name,
            "vatTaxCode": self.vat_tax_code,
            "status": self.status,
            "stepIndex": self.step_index,
            "parcels": [p.to_dict() for p in self.parcels] if self.parcels else [],
            "items": [it.to_dict() for it in self.items] if self.items else [],
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class OrderParcel(Base):
    """Bảng 13: order_parcels — Tách kiện hàng Multi-Vendor theo từng Shop & Lộ trình bưu tá."""
    __tablename__ = "order_parcels"

    id = Column(String(36), primary_key=True, default=lambda: f"pkg-{uuid.uuid4().hex[:8]}")
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    parcel_code = Column(String(30), unique=True, index=True, nullable=False)
    parcel_type = Column(String(20), nullable=False)  # 'mall_warehouse' | 'c2c_seller'
    carrier_name = Column(String(60), nullable=False)
    tracking_code = Column(String(40), unique=True, index=True, nullable=False)
    shipping_fee = Column(BigInteger, default=0, nullable=False)
    estimated_delivery = Column(String(80), nullable=True)
    status = Column(String(20), default="processing", nullable=False)  # 'processing', 'ready_for_pickup', 'in_transit', 'delivered', 'returned'
    created_at = Column(DateTime, default=func.now(), nullable=False)

    order = relationship("Order", back_populates="parcels")
    seller = relationship("User")
    items = relationship("OrderItem", back_populates="parcel", cascade="all, delete-orphan")
    tracking_events = relationship("OrderTrackingEvent", back_populates="parcel", cascade="all, delete-orphan", order_by="OrderTrackingEvent.event_time")

    def to_dict(self):
        return {
            "id": self.id,
            "orderId": self.order_id,
            "sellerId": self.seller_id,
            "sellerName": self.seller.full_name if self.seller else None,
            "parcelCode": self.parcel_code,
            "parcelType": self.parcel_type,
            "carrierName": self.carrier_name,
            "trackingCode": self.tracking_code,
            "shippingFee": self.shipping_fee,
            "estimatedDelivery": self.estimated_delivery,
            "status": self.status,
            "items": [it.to_dict() for it in self.items] if self.items else [],
            "trackingEvents": [ev.to_dict() for ev in self.tracking_events] if self.tracking_events else [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class OrderItem(Base):
    """Bảng 14: order_items — Chi tiết từng món hàng trong đơn hàng & kiện hàng."""
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: f"item-{uuid.uuid4().hex[:8]}")
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    parcel_id = Column(String(36), ForeignKey("order_parcels.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_type = Column(String(10), nullable=False)  # 'mall' | 'c2c'
    condition_pct = Column(Integer, default=100)
    unit_price = Column(BigInteger, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(BigInteger, nullable=False)
    variant_info = Column(String(100), default="")
    thumbnail_url = Column(Text, nullable=False)

    order = relationship("Order", back_populates="items")
    parcel = relationship("OrderParcel", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def to_dict(self):
        return {
            "id": self.id,
            "orderId": self.order_id,
            "parcelId": self.parcel_id,
            "productId": self.product_id,
            "productName": self.product_name,
            "productType": self.product_type,
            "conditionPct": self.condition_pct,
            "unitPrice": self.unit_price,
            "quantity": self.quantity,
            "totalPrice": self.total_price,
            "variantInfo": self.variant_info,
            "thumbnailUrl": self.thumbnail_url,
        }


class OrderTrackingEvent(Base):
    """Bảng 15: order_tracking_events — Nhật ký hành trình bưu kiện thời gian thực."""
    __tablename__ = "order_tracking_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parcel_id = Column(String(36), ForeignKey("order_parcels.id", ondelete="CASCADE"), nullable=False, index=True)
    status_title = Column(String(120), nullable=False)
    status_description = Column(Text, nullable=False)
    location = Column(String(120), nullable=False)
    shipper_name = Column(String(80), default="")
    shipper_phone = Column(String(20), default="")
    event_time = Column(DateTime, default=func.now(), nullable=False)

    parcel = relationship("OrderParcel", back_populates="tracking_events")

    def to_dict(self):
        return {
            "id": self.id,
            "parcelId": self.parcel_id,
            "statusTitle": self.status_title,
            "statusDescription": self.status_description,
            "location": self.location,
            "shipperName": self.shipper_name,
            "shipperPhone": self.shipper_phone,
            "eventTime": self.event_time.isoformat() if self.event_time else None,
        }
