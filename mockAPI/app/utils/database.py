"""
Database Session utils dùng chung cho mock DB
（Mock環境用DBセッション管理ユーティリティ）
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models import (
    mock_access_keys,
    mock_reference_status,
    mock_application_status,
    mock_message,
    mock_document
)
# ======================
# Database Config (Mock専用 SQLite)
# ======================
# Hiện tại dùng SQLite mock local → có thể dễ dàng đổi sang Postgres trong môi trường real integration test
SQLALCHEMY_DATABASE_URL = "sqlite:///./mock_db.sqlite3"

# Tạo SQLAlchemy Engine
# (check_same_thread=False → cho phép multi-thread access trong môi trường FastAPI development mode)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

# Session Factory tạo ra DB Session cho mỗi request
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """
    Dependency injection function (FastAPI chuẩn).
    Mỗi request API sẽ tạo mới 1 DB session, đảm bảo release sau khi xử lý xong.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
