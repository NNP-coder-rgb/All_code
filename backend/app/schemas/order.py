"""
order.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Đơn hàng & Tách kiện Multi-Vendor
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)
    offer_id: Optional[int] = None


class OrderCreateRequest(BaseModel):
    items: List[OrderItemRequest]
    shipping_address_id: Optional[int] = None
    recipient_name: str
    phone_number: str
    shipping_address: str
    shipping_carrier: str = "Giao Hàng Nhanh (GHN)"
    payment_method: str = Field(default="cod", description="cod, vnpay, momo, escrow_wallet")
    voucher_code: Optional[str] = None
    buyer_note: Optional[str] = None
    is_vat_invoice: bool = False
    vat_company_name: Optional[str] = None
    vat_tax_code: Optional[str] = None
    vat_company_address: Optional[str] = None


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="pending, confirmed, processing, shipping, delivered, completed, cancelled")
    note: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Schema thông tin sản phẩm trong từng kiện hàng."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    parcel_id: int
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    product_sku: Optional[str] = None
    condition_percentage: int = 100
    listing_type: str = "c2c_used"
    unit_price: float
    quantity: int
    subtotal: float


class OrderTrackingEventResponse(BaseModel):
    """Schema nhật ký hành trình vận chuyển kiện hàng."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    parcel_id: int
    event_status: str
    location: Optional[str] = None
    description: str
    event_time: Optional[datetime] = None


class OrderParcelResponse(BaseModel):
    """Schema kiện hàng được tách theo người bán (Multi-Vendor Split)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    seller_id: int
    parcel_code: str
    shipping_carrier: Optional[str] = None
    tracking_code: Optional[str] = None
    shipping_fee: float = 0.0
    status: str
    items: List[OrderItemResponse] = Field(default_factory=list)
    tracking_events: List[OrderTrackingEventResponse] = Field(default_factory=list)


class OrderResponse(BaseModel):
    """Schema chuẩn trả về thông tin Đơn hàng hoàn chỉnh."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_code: str
    buyer_id: int
    total_amount: float
    shipping_fee: float
    discount_amount: float
    final_amount: float
    payment_method: str
    payment_status: str
    status: str
    shipping_status: str
    recipient_name: str
    phone_number: str
    shipping_address: str
    buyer_note: Optional[str] = None
    is_vat_invoice: bool = False
    parcels: List[OrderParcelResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
