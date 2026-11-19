"""
products.py — Router xử lý Danh mục, Thương hiệu và Sản phẩm
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.catalog_service import catalog_service


def handle_get_categories(db: Session) -> Dict[str, Any]:
    categories = catalog_service.list_categories(db)
    return {
        "success": True,
        "message": "Lấy danh mục thành công",
        "data": [c.to_dict() for c in categories],
        "status_code": 200
    }


def handle_get_brands(db: Session) -> Dict[str, Any]:
    brands = catalog_service.list_brands(db)
    return {
        "success": True,
        "message": "Lấy thương hiệu thành công",
        "data": [b.to_dict() for b in brands],
        "status_code": 200
    }


def handle_get_products(db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
    category_slug = params.get("category")
    product_type = params.get("type")
    is_flash_sale = None
    if "flash" in params:
        is_flash_sale = params["flash"].lower() in ("true", "1")
    keyword = params.get("q") or params.get("search")
    min_price = int(params["min_price"]) if "min_price" in params and params["min_price"].isdigit() else None
    max_price = int(params["max_price"]) if "max_price" in params and params["max_price"].isdigit() else None
    limit = int(params.get("limit", 50))
    offset = int(params.get("offset", 0))

    products = catalog_service.list_products(
        db,
        category_slug=category_slug,
        product_type=product_type,
        is_flash_sale=is_flash_sale,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset
    )
    return {
        "success": True,
        "message": "Lấy danh sách sản phẩm thành công",
        "data": [p.to_dict() for p in products],
        "pagination": {
            "total_items": len(products),
            "limit": limit,
            "offset": offset
        },
        "status_code": 200
    }


def handle_get_product_detail(db: Session, identifier: str) -> Dict[str, Any]:
    product = catalog_service.get_product_by_id_or_slug(db, identifier)
    if not product:
        return {"success": False, "message": "Không tìm thấy sản phẩm", "status_code": 404}
    return {
        "success": True,
        "message": "Lấy chi tiết sản phẩm thành công",
        "data": product.to_dict(),
        "status_code": 200
    }
