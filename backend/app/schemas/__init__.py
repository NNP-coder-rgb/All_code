"""
app/schemas/__init__.py — Tập hợp và xuất toàn bộ Pydantic Response & Request Schemas
Tuân thủ đầy đủ tiêu chuẩn RESTful API, hỗ trợ serialization từ SQLAlchemy ORM Models.
"""

from app.schemas.common import (
    StandardResponse,
    PaginatedResponse,
    PaginationMeta,
    APIErrorDetail,
)
from app.schemas.user import (
    UserResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserUpdateRequest,
    UserAddressResponse,
    UserAddressCreateRequest,
    KYCVerificationResponse,
    KYCVerificationRequest,
    BankAccountResponse,
    BankAccountRequest,
)
from app.schemas.catalog import (
    CategoryResponse,
    BrandResponse,
    ProductResponse,
    ProductDetailResponse,
    ProductCreateRequest,
    ProductImageResponse,
    ProductSpecResponse,
)
from app.schemas.offer import (
    OfferResponse,
    OfferCreateRequest,
    OfferActionRequest,
)
from app.schemas.voucher import (
    VoucherResponse,
    VoucherValidateRequest,
    VoucherApplyResponse,
)
from app.schemas.order import (
    OrderResponse,
    OrderParcelResponse,
    OrderItemResponse,
    OrderTrackingEventResponse,
    OrderCreateRequest,
    OrderStatusUpdateRequest,
)
from app.schemas.escrow import (
    EscrowWalletResponse,
    EscrowTransactionResponse,
    WithdrawalRequest,
)
from app.schemas.dispute import (
    DisputeResponse,
    DisputeEvidenceResponse,
    DisputeMessageResponse,
    DisputeCreateRequest,
    DisputeMessageRequest,
    DisputeResolveRequest,
)
from app.schemas.interaction import (
    ProductReviewResponse,
    ProductReviewCreateRequest,
    ReviewReplyRequest,
    WishlistResponse,
    NotificationResponse,
)

__all__ = [
    # Common Envelopes
    "StandardResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "APIErrorDetail",

    # User & KYC
    "UserResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
    "UserUpdateRequest",
    "UserAddressResponse",
    "UserAddressCreateRequest",
    "KYCVerificationResponse",
    "KYCVerificationRequest",
    "BankAccountResponse",
    "BankAccountRequest",

    # Catalog & Product
    "CategoryResponse",
    "BrandResponse",
    "ProductResponse",
    "ProductDetailResponse",
    "ProductCreateRequest",
    "ProductImageResponse",
    "ProductSpecResponse",

    # Offer
    "OfferResponse",
    "OfferCreateRequest",
    "OfferActionRequest",

    # Voucher
    "VoucherResponse",
    "VoucherValidateRequest",
    "VoucherApplyResponse",

    # Order
    "OrderResponse",
    "OrderParcelResponse",
    "OrderItemResponse",
    "OrderTrackingEventResponse",
    "OrderCreateRequest",
    "OrderStatusUpdateRequest",

    # Escrow
    "EscrowWalletResponse",
    "EscrowTransactionResponse",
    "WithdrawalRequest",

    # Dispute
    "DisputeResponse",
    "DisputeEvidenceResponse",
    "DisputeMessageResponse",
    "DisputeCreateRequest",
    "DisputeMessageRequest",
    "DisputeResolveRequest",

    # Interaction
    "ProductReviewResponse",
    "ProductReviewCreateRequest",
    "ReviewReplyRequest",
    "WishlistResponse",
    "NotificationResponse",
]
