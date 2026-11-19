"""
voucher.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Module Khuyến mãi & Voucher
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class VoucherResponse(BaseModel):
    """Schema chuẩn trả về thông tin Voucher giảm giá."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    description: Optional[str] = None
    discount_type: str = Field(..., description="percentage hoặc fixed_amount")
    discount_value: float
    min_order_value: float = 0.0
    max_discount_amount: Optional[float] = None
    usage_limit: int = 1000
    used_count: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class VoucherValidateRequest(BaseModel):
    code: str
    order_amount: float


class VoucherApplyResponse(BaseModel):
    is_valid: bool
    discount_amount: float
    message: str
    voucher: Optional[VoucherResponse] = None
