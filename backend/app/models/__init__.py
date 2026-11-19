"""
app/models/__init__.py — Tập hợp và xuất toàn bộ 23 Models SQLAlchemy ORM cho Hệ thống Store-management
Bao gồm đầy đủ 100% các phân hệ nghiệp vụ theo giao diện Frontend.
"""

from app.models.user import User, KYCVerification, UserAddress, BankAccount
from app.models.catalog import Category, Brand, Product, ProductImage, ProductSpec
from app.models.offer import ProductOffer
from app.models.voucher import Voucher
from app.models.order import Order, OrderParcel, OrderItem, OrderTrackingEvent
from app.models.escrow import EscrowWallet, EscrowTransaction
from app.models.dispute import Dispute, DisputeEvidence, DisputeMessage
from app.models.interaction import ProductReview, Wishlist, Notification

__all__ = [
    # 1. Người dùng & Định danh eKYC
    "User",
    "KYCVerification",
    "UserAddress",
    "BankAccount",
    
    # 2. Danh mục, Thương hiệu & Sản phẩm Hybrid
    "Category",
    "Brand",
    "Product",
    "ProductImage",
    "ProductSpec",
    
    # 3. Trả giá C2C 24h
    "ProductOffer",
    
    # 4. Khuyến mãi & Voucher
    "Voucher",
    
    # 5. Đơn hàng & Tách kiện Multi-Vendor
    "Order",
    "OrderParcel",
    "OrderItem",
    "OrderTrackingEvent",
    
    # 6. Ví Ký Quỹ Escrow & Sổ cái 24/7
    "EscrowWallet",
    "EscrowTransaction",
    
    # 7. Phòng Trọng tài Khiếu nại 3 Bên
    "Dispute",
    "DisputeEvidence",
    "DisputeMessage",
    
    # 8. Đánh giá, Yêu thích & Thông báo
    "ProductReview",
    "Wishlist",
    "Notification",
]
