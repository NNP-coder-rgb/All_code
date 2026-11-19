"""
models/__init__.py — Tập hợp và xuất toàn bộ SQLAlchemy Models
Việc import tất cả models tại đây giúp Base.metadata tự động nhận diện
và tạo đầy đủ các bảng khi khởi chạy ứng dụng (Base.metadata.create_all).
"""

from core.database import Base
from models.user import User
from models.product import Product
from models.order import Order, OrderItem

__all__ = [
    "Base",
    "User",
    "Product",
    "Order",
    "OrderItem",
]
