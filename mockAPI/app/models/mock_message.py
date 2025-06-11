# app/models/mock_message.py
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timedelta, timezone
from app.models import Base


JST = timezone(timedelta(hours=9))

class MockMessage(Base):
    __tablename__ = "mock_messages"

    message_id        = Column(String(18), primary_key=True)
    reference_number  = Column(String(17))    # ← link tới Application
    message_type      = Column(String(1))     # 1,2,3,4,5,6,8
    title             = Column(String(255))
    content           = Column(String(8000))
    datetime          = Column(DateTime)
    document_id       = Column(String(18), nullable=True)
    is_new            = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(JST))