"""
config.py — Cấu hình ứng dụng tập trung (Central Application Settings)
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Hybrid Store E-Commerce Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Thư mục gốc & đường dẫn
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_DIR: str = os.path.join(BASE_DIR, "backend", "database")
    FRONTEND_DIR: str = os.path.join(BASE_DIR, "frontend")
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "backend", "uploads")
    
    # URL kết nối CSDL mặc định SQLite
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(DATABASE_DIR, 'hybrid_store.db').replace(os.sep, '/')}"
    )
    
    # Server Host & Port
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", 8000))
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")


settings = Settings()
