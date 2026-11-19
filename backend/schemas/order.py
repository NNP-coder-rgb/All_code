"""
schemas/order.py — Pydantic Schemas Cho Đối Tượng Đơn Hàng (Order)
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    unit_price: int
    quantity: int = Field(default=1, ge=1)


class OrderItemResponse(OrderItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subtotal: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Danh sách món hàng")
    shipping_fee: int = Field(default=0, ge=0)
    payment_method: str = Field(default="COD", description="COD, VNPay, Escrow")
    recipient_name: str = Field(..., min_length=2, max_length=100)
    recipient_phone: str = Field(..., min_length=9, max_length=20)
    shipping_address: str = Field(..., min_length=5)
    note: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    note: Optional[str] = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_code: str
    buyer_id: int
    total_amount: int
    shipping_fee: int
    payment_method: str
    payment_status: str
    status: str
    recipient_name: str
    recipient_phone: str
    shipping_address: str
    note: Optional[str] = None
    items: List[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
