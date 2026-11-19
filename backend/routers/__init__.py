"""
routers/__init__.py — Tập hợp và xuất toàn bộ APIRouter của Hệ thống
Tất cả các router phân hệ sẽ được gắn vào api_router chính và nạp vào FastAPI với tiền tố /api/v1.
"""

from fastapi import APIRouter

from routers.user_router import router as user_router
from routers.product_router import router as product_router
from routers.order_router import router as order_router

# Router chính tổng hợp toàn bộ các phân hệ API
api_router = APIRouter()

# Đăng ký các router con
api_router.include_router(user_router)
api_router.include_router(product_router)
api_router.include_router(order_router)

__all__ = [
    "api_router",
    "user_router",
    "product_router",
    "order_router",
]
