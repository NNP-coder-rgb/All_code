"""
core/config.py — Quản lý Cấu hình và Biến Môi trường Tập trung
Đọc các biến môi trường từ tệp .env bằng thư viện pydantic-settings.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


# Đường dẫn thư mục backend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ENV_FILE_PATH = os.path.join(BACKEND_DIR, ".env")


class Settings(BaseSettings):
    """Lớp cấu hình ứng dụng kế thừa từ BaseSettings của pydantic-settings."""
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH if os.path.exists(ENV_FILE_PATH) else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 1. Thông tin Chung của Ứng dụng
    PROJECT_NAME: str = "Hybrid Store E-Commerce Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="hybrid-store-jwt-secret-key-change-in-production", description="Khóa bí mật JWT")
    DEBUG: bool = True

    # 2. Cấu hình Máy chủ Web
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # 3. Cấu hình Cơ sở Dữ liệu MySQL (Driver pymysql)
    DB_HOST: str = Field(default="localhost", description="Địa chỉ máy chủ MySQL")
    DB_PORT: int = Field(default=3306, description="Cổng MySQL")
    DB_USER: str = Field(default="root", description="Tài khoản người dùng MySQL")
    DB_PASSWORD: str = Field(default="", description="Mật khẩu MySQL")
    DB_NAME: str = Field(default="hybrid_store_db", description="Tên Database MySQL")

    # Chuỗi kết nối trực tiếp tùy chọn (nếu có sẽ được ưu tiên sử dụng)
    DATABASE_URL: Optional[str] = None

    # Tự động Fallback sang SQLite nội bộ nếu MySQL chưa bật
    USE_SQLITE_FALLBACK: bool = True

    @property
    def database_url(self) -> str:
        """
        Sinh chuỗi kết nối SQLAlchemy:
        Ưu tiên DATABASE_URL trong .env, nếu không có thì sinh theo thông số MySQL (mysql+pymysql://...).
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Kết nối MySQL qua pymysql
        if self.DB_PASSWORD:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        return f"mysql+pymysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def sqlite_fallback_url(self) -> str:
        """Chuỗi kết nối SQLite dự phòng trong trường hợp MySQL chưa sẵn sàng."""
        db_path = os.path.join(BACKEND_DIR, "database", "hybrid_store.db").replace(os.sep, "/")
        return f"sqlite:///{db_path}"


# Khởi tạo đối tượng settings đơn lẻ (Singleton)
settings = Settings()
