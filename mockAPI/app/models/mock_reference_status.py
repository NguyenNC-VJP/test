# app/models/mock_reference_status.py

from sqlalchemy import Column, String, Integer, DateTime, Boolean
from app.models import Base
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))

class MockReferenceStatus(Base):
    """
    モック仮受付番号ステータスモデル
    polling 状況などを模擬する。
    """
    __tablename__ = "mock_reference_status"

    # 仮受付番号（20桁） - 主キー
    reference_number = Column(String(20), primary_key=True)

    # polling 回数（3回で "finished=True" になる）
    poll_count = Column(Integer, default=0)

    # 完了フラグ（未使用、将来拡張用）
    is_ready = Column(Boolean, default=False)

    # 作成日時
    created_at = Column(DateTime, default=lambda: datetime.now(JST))
