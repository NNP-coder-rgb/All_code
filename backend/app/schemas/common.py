"""
common.py — Cấu hình Response Schema dùng chung cho toàn bộ Hệ thống
Định chuẩn cấu trúc JSON trả về theo tiêu chuẩn RESTful API & Google JSON Style Guide.
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class APIErrorDetail(BaseModel):
    """Chi tiết lỗi chuẩn hoá trả về cho Client."""
    code: str = Field(default="BAD_REQUEST", description="Mã lỗi hệ thống định danh")
    message: str = Field(..., description="Thông báo lỗi thân thiện hiển thị cho người dùng")
    field: Optional[str] = Field(default=None, description="Trường dữ liệu gây lỗi (nếu có)")
    details: Optional[Any] = Field(default=None, description="Thông tin chi tiết gỡ lỗi (debug)")


class PaginationMeta(BaseModel):
    """Thông tin phân trang phân bổ đồng nhất."""
    page: int = Field(default=1, ge=1, description="Trang hiện tại")
    limit: int = Field(default=20, ge=1, le=100, description="Số lượng mục trên một trang")
    total_items: int = Field(default=0, ge=0, description="Tổng số mục tìm thấy")
    total_pages: int = Field(default=1, ge=0, description="Tổng số trang khả dụng")
    has_next: bool = Field(default=False, description="Còn trang tiếp theo hay không")
    has_prev: bool = Field(default=False, description="Có trang trước đó hay không")


class StandardResponse(BaseModel, Generic[T]):
    """
    Cấu trúc phản hồi chuẩn (Standard JSON Response Envelope) cho toàn bộ API đơn lẻ.
    Format:
    {
        "success": true,
        "message": "Thao tác thành công",
        "data": { ... },
        "error": null,
        "status_code": 200
    }
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    success: bool = Field(default=True, description="Trạng thái thực thi API")
    message: str = Field(default="Thao tác thành công", description="Thông điệp thông báo")
    data: Optional[T] = Field(default=None, description="Dữ liệu chính trả về")
    error: Optional[APIErrorDetail] = Field(default=None, description="Thông tin lỗi nếu thất bại")
    status_code: int = Field(default=200, description="Mã HTTP Status Code tương ứng")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Cấu trúc phản hồi chuẩn cho danh sách có phân trang.
    Format:
    {
        "success": true,
        "message": "Lấy danh sách thành công",
        "data": [ ... ],
        "pagination": { "page": 1, "limit": 20, "total_items": 100, "total_pages": 5, ... },
        "error": null,
        "status_code": 200
    }
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    success: bool = Field(default=True, description="Trạng thái thực thi API")
    message: str = Field(default="Lấy danh sách thành công", description="Thông điệp thông báo")
    data: List[T] = Field(default_factory=list, description="Danh sách dữ liệu bản ghi")
    pagination: PaginationMeta = Field(..., description="Dữ liệu siêu dữ liệu phân trang")
    error: Optional[APIErrorDetail] = Field(default=None, description="Thông tin lỗi nếu thất bại")
    status_code: int = Field(default=200, description="Mã HTTP Status Code tương ứng")
