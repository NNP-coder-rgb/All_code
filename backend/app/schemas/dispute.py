"""
dispute.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Phòng Trọng tài Khiếu nại 3 Bên
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DisputeEvidenceResponse(BaseModel):
    """Schema tài liệu chứng cứ (Video bóc hộp 4K, hình ảnh lỗi)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int
    uploader_id: int
    file_url: str
    file_type: str
    file_size_bytes: Optional[int] = None
    caption: Optional[str] = None
    created_at: Optional[datetime] = None


class DisputeMessageResponse(BaseModel):
    """Schema tin nhắn trao đổi trong phòng hòa giải trọng tài."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_id: int
    sender_id: int
    sender_role: str
    message: str
    attachment_url: Optional[str] = None
    created_at: Optional[datetime] = None


class DisputeResponse(BaseModel):
    """Schema chuẩn trả về thông tin Vụ án tranh chấp / khiếu nại."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dispute_code: str
    order_id: int
    buyer_id: int
    seller_id: int
    arbitrator_admin_id: Optional[int] = None
    reason: str
    description: str
    requested_solution: str
    refund_amount: float
    status: str
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None
    evidences: List[DisputeEvidenceResponse] = Field(default_factory=list)
    messages: List[DisputeMessageResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None


class DisputeCreateRequest(BaseModel):
    order_id: int
    reason: str
    description: str
    requested_solution: str = Field(default="full_refund", description="full_refund, partial_refund, return_goods")
    refund_amount: float
    evidence_urls: List[str] = Field(default_factory=list)


class DisputeMessageRequest(BaseModel):
    message: str
    attachment_url: Optional[str] = None


class DisputeResolveRequest(BaseModel):
    status: str = Field(..., description="resolved_refund_buyer, resolved_payout_seller, or rejected")
    resolution_note: str
    approved_refund_amount: Optional[float] = None
