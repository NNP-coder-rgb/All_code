"""
offer.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Module Trả giá C2C 24h
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OfferCreateRequest(BaseModel):
    product_id: int
    offered_price: float = Field(..., gt=0, description="Mức giá người mua đề xuất")
    message: Optional[str] = None


class OfferActionRequest(BaseModel):
    action: str = Field(..., description="accept, reject, hoặc counter")
    counter_price: Optional[float] = Field(default=None, description="Giá người bán đề xuất ngược lại")
    note: Optional[str] = None


class OfferResponse(BaseModel):
    """Schema chuẩn trả về thông tin Trả giá đàm phán 24h."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    buyer_id: int
    seller_id: int
    original_price: float
    offered_price: float
    discount_percentage: float
    message: Optional[str] = None
    status: str
    counter_price: Optional[float] = None
    expires_at: Optional[datetime] = None
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    created_at: Optional[datetime] = None
