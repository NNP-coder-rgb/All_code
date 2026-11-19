"""
models/offer.py — Model SQLAlchemy cho Phân hệ Thương Lượng & Trả Giá C2C (24 Giờ)
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductOffer(Base):
    """Bảng 10: product_offers — Lịch sử thương lượng giá giữa Người mua & Người bán."""
    __tablename__ = "product_offers"

    id = Column(String(36), primary_key=True, default=lambda: f"off-{uuid.uuid4().hex[:8]}")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_price = Column(BigInteger, nullable=False)
    offered_price = Column(BigInteger, nullable=False)
    discount_pct = Column(Integer, nullable=False)  # Tỉ lệ giảm % (vd: 12%)
    buyer_message = Column(Text, default="")
    seller_note = Column(Text, default="")
    status = Column(String(20), default="pending", nullable=False, index=True)  # 'pending', 'accepted', 'rejected', 'expired'
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    product = relationship("Product", back_populates="offers")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])

    def to_dict(self):
        return {
            "id": self.id,
            "productId": self.product_id,
            "productName": self.product.name if self.product else None,
            "productThumbnail": self.product.thumbnail_url if self.product else None,
            "buyerId": self.buyer_id,
            "buyerName": self.buyer.full_name if self.buyer else None,
            "sellerId": self.seller_id,
            "sellerName": self.seller.full_name if self.seller else None,
            "originalPrice": self.original_price,
            "offeredPrice": self.offered_price,
            "discountPct": self.discount_pct,
            "buyerMessage": self.buyer_message,
            "sellerNote": self.seller_note,
            "status": self.status,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
