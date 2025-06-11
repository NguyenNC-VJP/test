# app/models/mock_document.py
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timedelta, timezone
from app.models import Base

JST = timezone(timedelta(hours=9))

class MockDocument(Base):
    __tablename__ = "mock_documents"

    document_id  = Column(String(18), primary_key=True)
    file_path    = Column(String(255))   # path tới file pdf/zip
    verify_sign  = Column(String(20), default="Valid")  # Valid / Invalid / ...

    created_at = Column(DateTime, default=lambda: datetime.now(JST))