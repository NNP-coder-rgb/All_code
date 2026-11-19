"""
offers.py — Router xử lý Trả giá C2C 24h
"""

from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.offer import ProductOffer
from app.models.catalog import Product


def handle_create_offer(db: Session, body: Dict[str, Any]) -> Dict[str, Any]:
    product_id = body.get("product_id")
    buyer_id = body.get("buyer_id")
    offered_price = body.get("offered_price")
    buyer_message = body.get("buyer_message", "")

    if not product_id or not buyer_id or not offered_price:
        return {"success": False, "message": "Thiếu thông tin sản phẩm hoặc giá đề xuất", "status_code": 400}

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"success": False, "message": "Không tìm thấy sản phẩm", "status_code": 404}

    if not product.allow_offers:
        return {"success": False, "message": "Sản phẩm này không cho phép trả giá", "status_code": 400}

    discount_pct = int(round((1 - (offered_price / product.selling_price)) * 100))
    now = datetime.now(timezone.utc)
    offer = ProductOffer(
        product_id=product.id,
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        original_price=product.selling_price,
        offered_price=offered_price,
        discount_pct=discount_pct,
        buyer_message=buyer_message,
        status="pending",
        expires_at=now + timedelta(hours=24)
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)

    return {
        "success": True,
        "message": "Gửi yêu cầu trả giá thành công! Người bán có 24h để phản hồi.",
        "data": offer.to_dict(),
        "status_code": 201
    }


def handle_get_offers(db: Session, user_id: str) -> Dict[str, Any]:
    offers = (
        db.query(ProductOffer)
        .filter((ProductOffer.buyer_id == user_id) | (ProductOffer.seller_id == user_id))
        .order_by(ProductOffer.created_at.desc())
        .all()
    )
    return {
        "success": True,
        "message": "Lấy danh sách trả giá thành công",
        "data": [o.to_dict() for o in offers],
        "status_code": 200
    }
