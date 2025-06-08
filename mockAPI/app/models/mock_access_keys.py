"""
Model table dùng để lưu trữ tạm access_key mock (production-ready stateful DBテーブル定義)
"""

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

# ========================
# Khởi tạo Base ORM Model cho SQLAlchemy
# ========================
Base = declarative_base()

# ========================
# Định nghĩa timezone JST (日本標準時)
# ========================
JST = timezone(timedelta(hours=9))

class MockAccessKey(Base):
    """
    Table mock_access_keys:
    - Dùng lưu tạm toàn bộ access_key A / B trong suốt quá trình mock testing.
    - Giữ trạng thái access key để mô phỏng stateful giống môi trường production thật.
    """
    __tablename__ = 'mock_access_keys'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto PK ID
    access_key = Column(String(100), unique=True, nullable=False)  # Unique AccessKey (A or B)
    redirect_url = Column(String(1000), nullable=False)  # URL redirect mock GbizID
    created_at = Column(DateTime, default=lambda: datetime.now(JST))  # Thời điểm phát hành key (lưu timestamp chuẩn JST)
