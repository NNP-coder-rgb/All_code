"""
interaction.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Đánh giá, Yêu thích & Thông báo
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductReviewResponse(BaseModel):
    """Schema chuẩn trả về thông tin Đánh giá sản phẩm."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    order_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    review_images: Optional[str] = None
    is_verified_buyer: bool = True
    seller_reply: Optional[str] = None
    seller_replied_at: Optional[datetime] = None
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    created_at: Optional[datetime] = None


class ProductReviewCreateRequest(BaseModel):
    product_id: int
    order_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    comment: str
    review_images: Optional[List[str]] = Field(default_factory=list)


class ReviewReplyRequest(BaseModel):
    seller_reply: str


class WishlistResponse(BaseModel):
    """Schema chuẩn trả về danh sách sản phẩm yêu thích."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    created_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Schema chuẩn thông báo trung tâm (Notification Center)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    content: str
    type: str
    reference_id: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
