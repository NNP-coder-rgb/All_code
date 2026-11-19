"""
services/__init__.py — Tập hợp và xuất toàn bộ Services xử lý nghiệp vụ
"""

from services.user_service import user_service, UserService
from services.product_service import product_service, ProductService
from services.order_service import order_service, OrderService

__all__ = [
    "user_service",
    "UserService",
    "product_service",
    "ProductService",
    "order_service",
    "OrderService",
]
