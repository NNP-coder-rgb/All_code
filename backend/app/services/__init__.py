"""
app/services/__init__.py — Tập hợp các dịch vụ nghiệp vụ (Business Services)
"""

from app.services.auth_service import auth_service, AuthService
from app.services.catalog_service import catalog_service, CatalogService

__all__ = [
    "auth_service",
    "AuthService",
    "catalog_service",
    "CatalogService",
]
