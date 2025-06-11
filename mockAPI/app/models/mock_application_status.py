# app/models/mock_application_status.py

from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime, timedelta, timezone
from app.models import Base

JST = timezone(timedelta(hours=9))

class MockApplicationStatus(Base):
    """
    モック申請状況モデル
    厚生労働省（健康保険組合）用の申請データを模擬する。
    """
    __tablename__ = "mock_application_status"

    # 仮受付番号（17桁） - 主キー
    reference_number = Column(String(20), primary_key=True)

    # 法人情報（モック）
    corporate_name = Column(String(100))
    representative = Column(String(100))

    # 申請送信日時
    transmit_datetime = Column(DateTime)

    # 手続き（procedures）情報 - JSON array（status_code等）
    procedures = Column(JSON)

    # メッセージ情報（完了時のみ） - JSON array
    messages = Column(JSON)

    # 作成・更新管理
    created_at = Column(DateTime, default=lambda: datetime.now(JST))
    updated_at = Column(DateTime, default=lambda: datetime.now(JST), onupdate=lambda: datetime.now(JST))
