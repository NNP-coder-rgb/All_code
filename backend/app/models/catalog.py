"""
models/catalog.py — Models SQLAlchemy cho Danh Mục, Thương Hiệu, Sản Phẩm Hybrid, Hình Ảnh & Cấu Hình
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Category(Base):
    """Bảng 5: categories — Cây danh mục ngành hàng."""
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon = Column(String(40), default="category")
    tone = Column(String(20), default="primary")
    badge = Column(String(50), default="")
    desc = Column(Text, default="")
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    products = relationship("Product", back_populates="category")

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "icon": self.icon,
            "icon_name": self.icon,
            "tone": self.tone,
            "badge": self.badge,
            "desc": self.desc,
            "displayOrder": self.display_order,
            "isActive": self.is_active,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Brand(Base):
    """Bảng 6: brands — Thương hiệu chính hãng phân phối."""
    __tablename__ = "brands"

    id = Column(String(36), primary_key=True)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    logo_url = Column(Text, default="")
    is_official_mall = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    products = relationship("Product", back_populates="brand")

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "logoUrl": self.logo_url,
            "isOfficialMall": self.is_official_mall,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Product(Base):
    """Bảng 7: products — Bảng sản phẩm trung tâm (Brand Mall Mới 100% & Chợ C2C Like New)."""
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: f"p-{uuid.uuid4().hex[:8]}")
    sku = Column(String(40), unique=True, nullable=True)
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(120), nullable=True)
    slug = Column(String(255), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False, index=True)
    brand_id = Column(String(36), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    product_type = Column(String(10), default="mall", nullable=False, index=True)  # 'mall' | 'c2c'
    condition_pct = Column(Integer, default=100)  # 50 - 100%
    condition_label = Column(String(60), default="Mới 100%")
    original_price = Column(BigInteger, nullable=False)
    selling_price = Column(BigInteger, nullable=False, index=True)
    stock_quantity = Column(Integer, default=1, nullable=False)
    thumbnail_url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    accessories_included = Column(Text, default="")
    warranty_months = Column(Integer, default=12, nullable=False)
    warranty_policy_note = Column(Text, default="")
    inspection_passed = Column(Boolean, default=True, nullable=False)
    inspection_score = Column(Float, default=9.8)
    allow_offers = Column(Boolean, default=False, nullable=False)
    is_flash_sale = Column(Boolean, default=False, nullable=False)
    flash_sale_end = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0, nullable=False)
    sales_count = Column(Integer, default=0, nullable=False)
    rating_average = Column(Float, default=5.0, nullable=False)
    rating_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="active", nullable=False, index=True)  # 'active', 'sold_out', 'hidden', 'draft'
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    seller = relationship("User", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.display_order")
    specs = relationship("ProductSpec", back_populates="product", cascade="all, delete-orphan", order_by="ProductSpec.display_order")
    offers = relationship("ProductOffer", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "shortName": self.short_name,
            "slug": self.slug,
            "categoryId": self.category_id,
            "categoryName": self.category.name if self.category else None,
            "brandId": self.brand_id,
            "brandName": self.brand.name if self.brand else None,
            "sellerId": self.seller_id,
            "sellerName": self.seller.full_name if self.seller else None,
            "sellerAvatar": self.seller.avatar_url if self.seller else None,
            "productType": self.product_type,
            "conditionPct": self.condition_pct,
            "conditionLabel": self.condition_label,
            "originalPrice": self.original_price,
            "sellingPrice": self.selling_price,
            "price": self.selling_price,
            "stockQuantity": self.stock_quantity,
            "thumbnailUrl": self.thumbnail_url,
            "description": self.description,
            "accessoriesIncluded": self.accessories_included,
            "warrantyMonths": self.warranty_months,
            "warrantyPolicyNote": self.warranty_policy_note,
            "inspectionPassed": self.inspection_passed,
            "inspectionScore": self.inspection_score,
            "allowOffers": self.allow_offers,
            "isFlashSale": self.is_flash_sale,
            "flashSaleEnd": self.flash_sale_end.isoformat() if self.flash_sale_end else None,
            "viewCount": self.view_count,
            "salesCount": self.sales_count,
            "ratingAverage": self.rating_average,
            "ratingCount": self.rating_count,
            "status": self.status,
            "images": [img.image_url for img in self.images] if self.images else [self.thumbnail_url],
            "specs": {sp.spec_key: sp.spec_value for sp in self.specs} if self.specs else {},
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductImage(Base):
    """Bảng 8: product_images — Bộ sưu tập hình ảnh thực tế đa góc."""
    __tablename__ = "product_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    is_cover = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    product = relationship("Product", back_populates="images")


class ProductSpec(Base):
    """Bảng 9: product_specs — Bảng thông số kỹ thuật chi tiết theo thiết bị."""
    __tablename__ = "product_specs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    spec_key = Column(String(80), nullable=False)
    spec_value = Column(Text, nullable=False)
    group_name = Column(String(60), default="Cấu hình chung")
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="specs")
