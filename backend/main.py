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


# Middleware chống cache trình duyệt cho file HTML, JS, CSS
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.endswith((".html", ".js", ".css")) or path in ["/", "/index.html"]:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response



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
# TÍCH HỢP & PHỤC VỤ GIAO DIỆN FRONTEND TĨNH & FILE TẢI LÊN
# ==============================================================
ROOT_DIR = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
UPLOADS_DIR = os.path.join(CURRENT_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

if os.path.isdir(FRONTEND_DIR):
    for sub in ["assets", "css", "js", "pages", "components"]:
        sub_path = os.path.join(FRONTEND_DIR, sub)
        if os.path.isdir(sub_path):
            app.mount(f"/{sub}", StaticFiles(directory=sub_path), name=sub)

    @app.get("/", include_in_schema=False)
    @app.get("/index.html", include_in_schema=False)
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

    @app.get("/manifest.json", include_in_schema=False)
    def serve_manifest():
        manifest_file = os.path.join(FRONTEND_DIR, "manifest.json")
        if os.path.isfile(manifest_file):
            return FileResponse(manifest_file, media_type="application/json")
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    @app.get("/sw.js", include_in_schema=False)
    def serve_sw():
        sw_file = os.path.join(FRONTEND_DIR, "sw.js")
        if os.path.isfile(sw_file):
            return FileResponse(sw_file, media_type="application/javascript")
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    @app.get("/{filename:path}", include_in_schema=False)
    def serve_frontend_fallback(filename: str):
        # 1. Tránh ghi đè các endpoint API hoặc tài liệu Swagger
        if filename.startswith(("api/", "docs", "redoc", "openapi.json")):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        # 2. Kiểm tra nếu file tồn tại trực tiếp trong thư mục frontend
        file_path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # 3. Thử tìm file .html tương ứng
        html_file = os.path.join(FRONTEND_DIR, f"{filename}.html")
        if os.path.isfile(html_file):
            return FileResponse(html_file)

        # 4. Fallback về index.html cho SPA hoặc liên kết gốc
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)

        return JSONResponse(status_code=404, content={"detail": "Not Found"})
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
