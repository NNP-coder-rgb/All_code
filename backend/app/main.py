"""
main.py — Máy chủ Fullstack & RESTful API Backend cho Sàn TMĐT Hybrid Store
Được xây dựng trên nền tảng SQLAlchemy ORM Models (23 Bảng Chuẩn) & Pydantic Response Schemas.
Hỗ trợ chạy trực tiếp với Python 3 tiêu chuẩn (Zero-External Dependency Server).
"""

import json
import os
import sys
import mimetypes
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket

# Thêm đường dẫn backend vào sys.path để import chuẩn
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = CURRENT_DIR
BACKEND_DIR = os.path.dirname(APP_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.database import engine, Base, SessionLocal, create_all_tables
import app.models
from app.routers import (
    handle_login, handle_register, handle_profile,
    handle_get_categories, handle_get_brands, handle_get_products, handle_get_product_detail,
    handle_create_offer, handle_get_offers,
    handle_get_orders, handle_get_order_detail,
    handle_get_wallet,
    handle_get_disputes, handle_get_dispute_detail,
    handle_get_vouchers
)

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))

# Tự động tạo 23 bảng nếu chưa có
create_all_tables()


class HybridStoreAPIHandler(BaseHTTPRequestHandler):
    """Bộ xử lý HTTP cho RESTful API và Tĩnh Frontend."""

    def _set_cors_headers(self, status_code=200, content_type="application/json; charset=utf-8"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_cors_headers(200)

    def _send_json(self, data: dict, status_code=200):
        code = data.get("status_code", status_code)
        self._set_cors_headers(code)
        res_bytes = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.wfile.write(res_bytes)

    def _read_body_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                raw = self.rfile.read(length).decode("utf-8")
                return json.loads(raw)
        except Exception:
            pass
        return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = dict(urllib.parse.parse_qsl(parsed.query))

        db = SessionLocal()
        try:
            # API Endpoints
            if path == "/api/health":
                self._send_json({"success": True, "message": "Hybrid Store API Backend is Healthy", "status_code": 200})
                return

            if path == "/api/categories":
                res = handle_get_categories(db)
                self._send_json(res)
                return

            if path == "/api/brands":
                res = handle_get_brands(db)
                self._send_json(res)
                return

            if path == "/api/products":
                res = handle_get_products(db, query)
                self._send_json(res)
                return

            if path.startswith("/api/products/"):
                identifier = path.replace("/api/products/", "").strip()
                res = handle_get_product_detail(db, identifier)
                self._send_json(res)
                return

            if path == "/api/vouchers":
                res = handle_get_vouchers(db)
                self._send_json(res)
                return

            if path == "/api/offers":
                user_id = query.get("userId", "usr-tuan")
                res = handle_get_offers(db, user_id)
                self._send_json(res)
                return

            if path == "/api/orders":
                user_id = query.get("userId", "usr-tuan")
                res = handle_get_orders(db, user_id)
                self._send_json(res)
                return

            if path.startswith("/api/orders/"):
                identifier = path.replace("/api/orders/", "").strip()
                res = handle_get_order_detail(db, identifier)
                self._send_json(res)
                return

            if path == "/api/escrow/wallet":
                user_id = query.get("userId", "usr-minh")
                res = handle_get_wallet(db, user_id)
                self._send_json(res)
                return

            if path == "/api/disputes":
                user_id = query.get("userId", "usr-tuan")
                res = handle_get_disputes(db, user_id)
                self._send_json(res)
                return

            if path.startswith("/api/disputes/"):
                identifier = path.replace("/api/disputes/", "").strip()
                res = handle_get_dispute_detail(db, identifier)
                self._send_json(res)
                return

            if path.startswith("/api/users/profile"):
                user_id = query.get("userId", "usr-tuan")
                res = handle_profile(db, user_id)
                self._send_json(res)
                return

        finally:
            db.close()

        # Phục vụ Frontend Static Files
        self._serve_static_file(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_body_json()

        db = SessionLocal()
        try:
            if path == "/api/auth/login":
                res = handle_login(db, body)
                self._send_json(res)
                return

            if path == "/api/auth/register":
                res = handle_register(db, body)
                self._send_json(res)
                return

            if path == "/api/offers":
                res = handle_create_offer(db, body)
                self._send_json(res)
                return

            self._send_json({"success": False, "message": f"Endpoint không tìm thấy: {path}", "status_code": 404})
        finally:
            db.close()

    def _serve_static_file(self, req_path: str):
        if req_path == "/" or req_path == "":
            req_path = "/index.html"

        safe_path = req_path.lstrip("/").replace("/", os.sep)
        full_path = os.path.join(FRONTEND_DIR, safe_path)

        if not os.path.isfile(full_path):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        if mime_type.startswith("text/") or mime_type in ("application/javascript", "application/json"):
            mime_type += "; charset=utf-8"

        try:
            with open(full_path, "rb") as f:
                content = f.read()
            self._set_cors_headers(200, mime_type)
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"500 Internal Error: {e}".encode("utf-8"))


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_server(port=PORT):
    local_ip = get_local_ip()
    server_address = (HOST, port)
    
    try:
        httpd = ThreadingHTTPServer(server_address, HybridStoreAPIHandler)
    except Exception:
        port = 8080
        server_address = (HOST, port)
        httpd = ThreadingHTTPServer(server_address, HybridStoreAPIHandler)

    print("=" * 68)
    print("🚀 MÁY CHỦ SÀN TMĐT HYBRID STORE HOẠT ĐỘNG (PYTHON + SQLALCHEMY)")
    print(f"📁 Database: SQLite 23 Bảng ORM ({os.path.join(BACKEND_DIR, 'database', 'hybrid_store.db')})")
    print(f"💻 Truy cập máy tính:  http://127.0.0.1:{port}/")
    print(f"💻 Link Localhost:    http://localhost:{port}/")
    print(f"📱 Mạng LAN / Wi-Fi:  http://{local_ip}:{port}/")
    print(f"🛒 Kênh Người Bán:    http://127.0.0.1:{port}/pages/seller/dashboard.html")
    print(f"🔍 API Health:        http://127.0.0.1:{port}/api/health")
    print(f"📦 API Products:      http://127.0.0.1:{port}/api/products")
    print("=" * 68)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang tắt máy chủ...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
