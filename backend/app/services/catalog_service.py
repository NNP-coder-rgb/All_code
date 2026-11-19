"""
catalog_service.py — Nghiệp vụ Danh mục, Thương hiệu và Sản phẩm Hybrid
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.catalog import Category, Brand, Product, ProductImage, ProductSpec


class CatalogService:
    @staticmethod
    def list_categories(db: Session) -> List[Category]:
        return db.query(Category).filter(Category.is_active == True).order_by(Category.display_order).all()

    @staticmethod
    def list_brands(db: Session) -> List[Brand]:
        return db.query(Brand).order_by(Brand.name).all()

    @staticmethod
    def list_products(
        db: Session,
        category_slug: Optional[str] = None,
        product_type: Optional[str] = None,
        is_flash_sale: Optional[bool] = None,
        keyword: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Product]:
        query = db.query(Product).filter(Product.status == "active")

        if category_slug:
            cat = db.query(Category).filter(Category.slug == category_slug).first()
            if cat:
                query = query.filter(Product.category_id == cat.id)

        if product_type:
            query = query.filter(Product.product_type == product_type)

        if is_flash_sale is not None:
            query = query.filter(Product.is_flash_sale == is_flash_sale)

        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(or_(Product.name.ilike(kw), Product.short_name.ilike(kw), Product.description.ilike(kw)))

        if min_price is not None:
            query = query.filter(Product.selling_price >= min_price)

        if max_price is not None:
            query = query.filter(Product.selling_price <= max_price)

        return query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_product_by_id_or_slug(db: Session, identifier: str) -> Optional[Product]:
        return (
            db.query(Product)
            .filter(or_(Product.id == identifier, Product.slug == identifier))
            .first()
        )


catalog_service = CatalogService()
