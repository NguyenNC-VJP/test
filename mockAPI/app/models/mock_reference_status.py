# app/models/mock_reference_status.py

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()
JST = timezone(timedelta(hours=9))

class MockReferenceStatus(Base):
    __tablename__ = "mock_reference_status"

    reference_number = Column(String(20), primary_key=True)
    poll_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(JST))
