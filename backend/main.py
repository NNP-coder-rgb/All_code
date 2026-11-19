"""
main.py — Điểm Khởi Chạy Ứng Dụng FastAPI Backend
Cấu hình CORS Middleware, Tự động khởi tạo bảng CSDL (create_all),
Đăng ký các API Routers với tiền tố /api/v1, Swagger UI /docs và phục vụ Giao diện Frontend.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Thêm thư mục backend vào sys.path để import chuẩn theo kiến trúc phân tầng
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.config import settings
from core.database import engine, Base, create_all_tables
from routers import api_router


# ==============================================================
# LIFESPAN: QUẢN LÝ VÒNG ĐỜI ỨNG DỤNG (STARTUP & SHUTDOWN)
# ==============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý sự kiện khởi động và tắt ứng dụng:
    Tự động gọi Base.metadata.create_all(bind=engine) để sinh bảng trong Database.
    """
    print("=" * 68)
    print(f"🚀 KHỞI ĐỘNG ỨNG DỤNG: {settings.PROJECT_NAME} (v{settings.VERSION})")
    print(f"📁 CSDL Kết nối: {settings.database_url}")
    print("=" * 68)

    # 1. Tự động đồng bộ các bảng trong CSDL thông qua SQLAlchemy ORM
    try:
        create_all_tables()
        print("✅ [SQLAlchemy] Toàn bộ bảng cơ sở dữ liệu đã sẵn sàng.")
    except Exception as e:
        print(f"⚠️ [SQLAlchemy] Lỗi khi tạo bảng CSDL: {e}")

    yield

    print("🛑 [FastAPI] Ứng dụng đang dừng hoạt động...")


# ==============================================================
# KHỞI TẠO ỨNG DỤNG FASTAPI
# ==============================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống Backend RESTful API Sàn TMĐT Hybrid Store xây dựng theo kiến trúc phân tầng (FastAPI + SQLAlchemy + MySQL)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ==============================================================
# CẤU HÌNH CORS MIDDLEWARE (CHO PHÉP FRONTEND KẾT NỐI AN TOÀN)
# ==============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================
# ĐĂNG KÝ CÁC ROUTERS VỚI TIỀN TỐ /api/v1
# ==============================================================
app.include_router(api_router, prefix=settings.API_V1_STR)


# ==============================================================
# ENDPOINTS HỆ THỐNG & HEALTH CHECK
# ==============================================================
@app.get(
    "/api/v1/health",
    tags=["System"],
    summary="Kiểm tra trạng thái máy chủ (Health Check)"
)
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }


# ==============================================================
# TÍCH HỢP & PHỤC VỤ GIAO DIỆN FRONTEND TĨNH (NẾU CÓ)
# ==============================================================
ROOT_DIR = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

if os.path.isdir(FRONTEND_DIR):
    for sub in ["assets", "css", "js", "pages", "components"]:
        sub_path = os.path.join(FRONTEND_DIR, sub)
        if os.path.isdir(sub_path):
            app.mount(f"/{sub}", StaticFiles(directory=sub_path), name=sub)

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {
            "message": f"Chào mừng đến với {settings.PROJECT_NAME}",
            "docs": "/docs",
            "redoc": "/redoc",
            "api_v1": settings.API_V1_STR
        }
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "message": f"Chào mừng đến với {settings.PROJECT_NAME}",
            "docs": "/docs",
            "redoc": "/redoc",
            "api_v1": settings.API_V1_STR
        }


# ==============================================================
# KHỞI CHẠY BẰNG UVICORN SERVER
# ==============================================================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
