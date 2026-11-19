"""
app/routers/__init__.py — Tập hợp các Router xử lý API
"""

from app.routers.auth import handle_login, handle_register, handle_profile
from app.routers.products import handle_get_categories, handle_get_brands, handle_get_products, handle_get_product_detail
from app.routers.offers import handle_create_offer, handle_get_offers
from app.routers.orders import handle_get_orders, handle_get_order_detail
from app.routers.escrow import handle_get_wallet
from app.routers.disputes import handle_get_disputes, handle_get_dispute_detail
from app.routers.vouchers import handle_get_vouchers

__all__ = [
    "handle_login",
    "handle_register",
    "handle_profile",
    "handle_get_categories",
    "handle_get_brands",
    "handle_get_products",
    "handle_get_product_detail",
    "handle_create_offer",
    "handle_get_offers",
    "handle_get_orders",
    "handle_get_order_detail",
    "handle_get_wallet",
    "handle_get_disputes",
    "handle_get_dispute_detail",
    "handle_get_vouchers",
]
