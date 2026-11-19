"""
routers/user_router.py — API Endpoints Quản Lý Người Dùng (Luồng CRUD Mẫu Chuẩn)
Tuân thủ nguyên tắc: Nhận request -> Validate qua schemas -> Gọi services -> Trả response chuẩn & HTTP Status Code.
"""

from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.common import BaseResponse, PaginatedResponse
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users (Quản lý người dùng)"])


@router.get(
    "/",
    response_model=PaginatedResponse[UserResponse],
    summary="Lấy danh sách người dùng có phân trang",
    description="Truy vấn danh sách người dùng hệ thống kèm bộ lọc vai trò (role) và từ khóa tìm kiếm (search)."
)
def get_users(
    page: Annotated[int, Query(ge=1, description="Số thứ tự trang")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Số bản ghi trên mỗi trang")] = 20,
    role: Annotated[Optional[str], Query(description="Lọc theo vai trò: buyer, seller, admin")] = None,
    search: Annotated[Optional[str], Query(description="Tìm kiếm theo tên, email, sđt")] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    users, total = user_service.get_users(db, skip=skip, limit=limit, role=role, search=search)
    return PaginatedResponse[UserResponse](
        success=True,
        message="Lấy danh sách người dùng thành công",
        data=users,
        total=total,
        page=page,
        limit=limit
    )


@router.get(
    "/{user_id}",
    response_model=BaseResponse[UserResponse],
    summary="Lấy thông tin chi tiết một người dùng",
    responses={
        404: {"description": "Không tìm thấy người dùng với ID đã cung cấp"}
    }
)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng có mã ID: {user_id}"
        )
    return BaseResponse[UserResponse](
        success=True,
        message="Lấy thông tin người dùng thành công",
        data=user
    )


@router.post(
    "/",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới một người dùng",
    responses={
        400: {"description": "Email hoặc số điện thoại đã tồn tại trên hệ thống"}
    }
)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra trùng lặp Email
    if user_service.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Địa chỉ email '{user_in.email}' đã được đăng ký trên hệ thống"
        )

    # 2. Kiểm tra trùng lặp Số điện thoại
    if user_service.get_by_phone(db, phone=user_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Số điện thoại '{user_in.phone}' đã được đăng ký tài khoản"
        )

    # 3. Gọi service thực hiện lưu vào CSDL
    new_user = user_service.create_user(db, user_in=user_in)
    return BaseResponse[UserResponse](
        success=True,
        message="Tạo mới tài khoản người dùng thành công",
        data=new_user
    )


@router.put(
    "/{user_id}",
    response_model=BaseResponse[UserResponse],
    summary="Cập nhật thông tin người dùng",
    responses={
        404: {"description": "Không tìm thấy người dùng cần cập nhật"}
    }
)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    updated_user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng có mã ID: {user_id} để cập nhật"
        )
    return BaseResponse[UserResponse](
        success=True,
        message="Cập nhật thông tin người dùng thành công",
        data=updated_user
    )


@router.delete(
    "/{user_id}",
    response_model=BaseResponse[dict],
    summary="Xóa người dùng khỏi hệ thống",
    responses={
        404: {"description": "Không tìm thấy người dùng cần xóa"}
    }
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = user_service.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng có mã ID: {user_id} để xóa"
        )
    return BaseResponse[dict](
        success=True,
        message=f"Đã xóa thành công người dùng có mã ID: {user_id}",
        data={"deleted_user_id": user_id}
    )
