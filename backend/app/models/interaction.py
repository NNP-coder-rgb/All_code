"""
models/interaction.py — Models SQLAlchemy cho Đánh Giá Sản Phẩm, Danh Sách Yêu Thích & Hộp Thư Thông Báo
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductReview(Base):
    """Bảng 21: product_reviews — Đánh giá chất lượng từ người mua thực tế & Huy hiệu Verified Buyer."""
    __tablename__ = "product_reviews"

    id = Column(String(36), primary_key=True, default=lambda: f"rev-{uuid.uuid4().hex[:8]}")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1 - 5 sao
    comment = Column(Text, nullable=False)
    has_photo = Column(Boolean, default=False, nullable=False)
    is_verified_buyer = Column(Boolean, default=True, nullable=False)
    seller_reply = Column(Text, default="")
    seller_replied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    order = relationship("Order")

    def to_dict(self):
        return {
            "id": self.id,
            "productId": self.product_id,
            "orderId": self.order_id,
            "userId": self.user_id,
            "authorName": self.user.full_name if self.user else "Người dùng",
            "authorAvatar": self.user.avatar_url if self.user else None,
            "rating": self.rating,
            "comment": self.comment,
            "hasPhoto": self.has_photo,
            "isVerifiedBuyer": self.is_verified_buyer,
            "sellerReply": self.seller_reply,
            "sellerRepliedAt": self.seller_replied_at.isoformat() if self.seller_replied_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Wishlist(Base):
    """Bảng 22: wishlists — Danh sách sản phẩm yêu thích của người dùng."""
    __tablename__ = "wishlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_wishlist"),
    )

    user = relationship("User", back_populates="wishlists")
    product = relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "productId": self.product_id,
            "product": self.product.to_dict() if self.product else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Notification(Base):
    """Bảng 23: notifications — Trung tâm thông báo cá nhân đa kênh."""
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: f"notif-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # 'order', 'promo', 'dispute', 'system'
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    link_url = Column(Text, default="")
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "linkUrl": self.link_url,
            "isRead": self.is_read,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
