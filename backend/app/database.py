"""
database.py — Cấu hình kết nối Cơ sở dữ liệu và Session qua SQLAlchemy
Hỗ trợ SQLite / PostgreSQL / MySQL thông qua DATABASE_URL.
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Đường dẫn thư mục
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = CURRENT_DIR
BACKEND_DIR = os.path.dirname(APP_DIR)
DATABASE_DIR = os.path.join(BACKEND_DIR, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

# URL kết nối CSDL (mặc định SQLite database/hybrid_store.db)
DB_PATH = os.path.join(DATABASE_DIR, "hybrid_store.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH.replace(os.sep, '/')}")

# Khởi tạo SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

# Kích hoạt Foreign Keys cho SQLite
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Sessionmaker quản lý phiên kết nối
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base cho toàn bộ Models
Base = declarative_base()


def get_db():
    """Dependency generator cho FastAPI / REST endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    """Context manager an toàn: tự động commit khi thành công, rollback khi có lỗi."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all_tables():
    """
    Tự động kết nối và tạo toàn bộ 23 bảng trong CSDL thông qua SQLAlchemy ORM Models.
    Không cần chạy lệnh raw SQL thủ công.
    """
    import app.models  # Nạp toàn bộ models để Base.metadata nhận diện
    Base.metadata.create_all(bind=engine)
    total_tables = len(Base.metadata.tables)
    print(f"✅ [SQLAlchemy] Đã tạo thành công {total_tables} bảng CSDL vào: {DB_PATH}")
    return total_tables


if __name__ == "__main__":
    create_all_tables()
