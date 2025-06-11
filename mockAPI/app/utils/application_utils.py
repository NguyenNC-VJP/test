# app/utils/application_utils.py

from datetime import datetime, timedelta, timezone
import uuid
import random
from sqlalchemy.orm import Session
from app.models.mock_application_status import MockApplicationStatus

JST = timezone(timedelta(hours=9))

# Status code pattern C (厚生労働省)
STATUS_CODE_PATTERN_C = ["001", "002", "003", "008"]

STATUS_NAME_MAP = {
    "001": "送信待ち",
    "002": "処理中",
    "003": "終了",
    "008": "要再申請"
}

def generate_mock_application_data(reference_number: str):
    """
    Tạo dữ liệu mock cho申請状況, theo pattern C
    - transmit_datetime → dạng datetime để lưu vào DB
    - metadata_contents_datetime → dùng isoformat vì nằm trong JSON
    """
    status_code = random.choice(STATUS_CODE_PATTERN_C)

    # Danh sách procedure mock (dạng JSON)
    procedures = [
        {
            "submission_name": "麻布税務署",
            "procedure_name": "法人設立届出",
            "metadata_code": "printdata_cache",
            "status_code": status_code,
            "status_name": STATUS_NAME_MAP.get(status_code, "不明"),
            "metadata_contents_datetime": (datetime.now(JST) - timedelta(days=1)).isoformat(),  # OK vì nằm trong JSON
            "metadata_end_datetime": None
        }
    ]

    # Danh sách message mock nếu status yêu cầu
    messages = []
    if status_code in ["003", "008"]:
        messages.append({
            "message_id": str(uuid.uuid4()),
            "message_type": "3",
            "new_arrivals": True,
            "datetime": datetime.now(JST).isoformat(),  # OK vì nằm trong JSON
            "title": "ファイル受領のお知らせがあります",
            "document_id": str(uuid.uuid4())
        })

    # Trả về dữ liệu cho model MockApplicationStatus
    return {
        "reference_number": reference_number,
        "corporate_name": "株式会社VTIジャパン",
        "representative": "代表取締役 チャン・スアン・コイ",
        "transmit_datetime": datetime.now(JST) - timedelta(days=2), 
        "procedures": procedures,
        "messages": messages
    }

def get_application_status(db: Session, reference_number: str):
    """Lấy thông tin application status từ DB, nếu không có thì tạo mới"""
    app_status = db.query(MockApplicationStatus).filter_by(reference_number=reference_number).first()

    if not app_status:
        mock_data = generate_mock_application_data(reference_number)
        app_status = MockApplicationStatus(**mock_data)
        db.add(app_status)
        db.commit()
        db.refresh(app_status)

    return app_status
