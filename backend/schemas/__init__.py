"""
schemas/__init__.py — Xuất toàn bộ Pydantic Request & Response Schemas
"""

from schemas.common import BaseResponse, PaginatedResponse
from schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from schemas.product import ProductBase, ProductCreate, ProductUpdate, ProductResponse
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderItemCreate, OrderItemResponse

__all__ = [
    "BaseResponse",
    "PaginatedResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderItemCreate",
    "OrderItemResponse",
]
