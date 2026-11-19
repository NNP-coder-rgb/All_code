"""
routers/order_router.py — API Endpoints Quản Lý Đơn Hàng (Orders)
"""

from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.common import BaseResponse, PaginatedResponse
from schemas.order import OrderCreate, OrderUpdate, OrderResponse
from services.order_service import order_service

router = APIRouter(prefix="/orders", tags=["Orders (Đơn hàng)"])


@router.get("/", response_model=PaginatedResponse[OrderResponse], summary="Lấy danh sách đơn hàng")
def get_orders(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    buyer_id: Annotated[Optional[int], Query(description="Lọc theo mã người mua")] = None,
    status_filter: Annotated[Optional[str], Query(alias="status", description="Lọc theo trạng thái")] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    orders, total = order_service.get_orders(db, buyer_id=buyer_id, status=status_filter, skip=skip, limit=limit)
    return PaginatedResponse[OrderResponse](
        success=True,
        message="Lấy danh sách đơn hàng thành công",
        data=orders,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{order_id}", response_model=BaseResponse[OrderResponse], summary="Chi tiết đơn hàng")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Không tìm thấy đơn hàng #{order_id}")
    return BaseResponse[OrderResponse](success=True, message="Lấy chi tiết đơn hàng thành công", data=order)


@router.post("/", response_model=BaseResponse[OrderResponse], status_code=status.HTTP_201_CREATED, summary="Khởi tạo đơn hàng mới")
def create_order(
    order_in: OrderCreate,
    buyer_id: int = Query(..., description="ID người mua thực hiện đặt hàng"),
    db: Session = Depends(get_db)
):
    order = order_service.create_order(db, buyer_id=buyer_id, order_in=order_in)
    return BaseResponse[OrderResponse](success=True, message="Đặt đơn hàng thành công", data=order)
