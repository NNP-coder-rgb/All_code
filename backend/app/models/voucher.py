"""
models/voucher.py — Model SQLAlchemy cho Phân hệ Khuyến Mãi, Mã Giảm Giá & Freeship
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Voucher(Base):
    """Bảng 11: vouchers — Kho phiếu ưu đãi toàn sàn."""
    __tablename__ = "vouchers"

    id = Column(String(36), primary_key=True, default=lambda: f"vch-{uuid.uuid4().hex[:8]}")
    code = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(120), nullable=False)
    voucher_type = Column(String(20), nullable=False)  # 'percent' | 'fixed' | 'freeship'
    discount_value = Column(BigInteger, nullable=False)
    min_order_value = Column(BigInteger, default=0, nullable=False)
    max_discount_amount = Column(BigInteger, nullable=True)
    usage_limit = Column(Integer, default=1000)
    usage_count = Column(Integer, default=0, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    orders = relationship("Order", back_populates="voucher")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "voucherType": self.voucher_type,
            "discountType": self.voucher_type,
            "discountValue": self.discount_value,
            "minOrderValue": self.min_order_value,
            "maxDiscountAmount": self.max_discount_amount,
            "usageLimit": self.usage_limit,
            "usageCount": self.usage_count,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
