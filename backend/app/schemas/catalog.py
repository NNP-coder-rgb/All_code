"""
catalog.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Danh mục, Thương hiệu & Sản phẩm Hybrid
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryResponse(BaseModel):
    """Schema chuẩn trả về thông tin Danh mục sản phẩm."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    icon_class: Optional[str] = None
    tone: Optional[str] = None
    badge: Optional[str] = None
    parent_id: Optional[int] = None
    display_order: int = 0
    is_active: bool = True
    total_products: int = 0


class BrandResponse(BaseModel):
    """Schema chuẩn trả về thông tin Thương hiệu chính hãng."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_official_mall: bool = False


class ProductSpecResponse(BaseModel):
    """Schema thông số kỹ thuật chi tiết của sản phẩm."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    spec_group: Optional[str] = None
    spec_name: str
    spec_value: str
    display_order: int = 0


class ProductImageResponse(BaseModel):
    """Schema thư viện hình ảnh đa góc chụp của sản phẩm."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    is_cover: bool = False
    display_order: int = 0


class ProductResponse(BaseModel):
    """Schema chuẩn trả về thông tin sản phẩm trên danh sách / thẻ card."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    category_id: int
    brand_id: Optional[int] = None
    name: str
    slug: str
    sku: Optional[str] = None
    listing_type: str
    condition_percentage: int
    condition_detail: Optional[str] = None
    original_price: float
    sale_price: float
    stock_quantity: int
    is_allow_bargain: bool = True
    min_bargain_price: Optional[float] = None
    cover_image: Optional[str] = None
    video_url: Optional[str] = None
    warranty_months: int = 0
    is_free_shipping: bool = False
    is_featured: bool = False
    inspection_score: Optional[int] = None
    rating_average: float = 5.0
    rating_count: int = 0
    sold_count: int = 0
    status: str = "active"
    created_at: Optional[datetime] = None


class ProductDetailResponse(ProductResponse):
    """Schema chi tiết đầy đủ khi người dùng xem trang chi tiết sản phẩm."""
    description: Optional[str] = None
    inspection_report: Optional[str] = None
    images: List[ProductImageResponse] = Field(default_factory=list)
    specs: List[ProductSpecResponse] = Field(default_factory=list)
    seller_info: Optional[Dict[str, Any]] = None
    category_info: Optional[Dict[str, Any]] = None
    brand_info: Optional[Dict[str, Any]] = None


class ProductCreateRequest(BaseModel):
    """Yêu cầu đăng tải sản phẩm mới từ Người bán."""
    category_id: int
    brand_id: Optional[int] = None
    name: str
    listing_type: str = Field(default="c2c_used", description="official_mall hoặc c2c_used")
    condition_percentage: int = Field(default=99, ge=1, le=100)
    condition_detail: Optional[str] = None
    original_price: float
    sale_price: float
    stock_quantity: int = 1
    is_allow_bargain: bool = True
    min_bargain_price: Optional[float] = None
    cover_image: str
    description: Optional[str] = None
    warranty_months: int = 0
    is_free_shipping: bool = False
    images: List[str] = Field(default_factory=list)
    specs: List[Dict[str, str]] = Field(default_factory=list)
