# app/api/routes/inquiries/message_application.py
"""
メッセージ詳細取得API (Mock)
--------------------------------------------
- URL:   /inquiries/message_application/{message_id}
- Method: GET
- Spec:  別紙10_メッセージ詳細取得API仕様 1.64
"""

import uuid
from fastapi import APIRouter, Path, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.access_key_utils import is_valid_access_key_b
from app.utils.error_response_builder import build_error_response
from app.models.mock_message import MockMessage
from app.models.mock_document import MockDocument

router = APIRouter()

@router.get("/inquiries/message_application/{message_id}")
def get_message_detail(
    message_id: str = Path(..., min_length=18, max_length=18),
    x_access_key: str = Header(..., alias="X-Access-Key"),
    db: Session = Depends(get_db)
):
    # ① Validate access key (pattern B)
    if not is_valid_access_key_b(x_access_key):
        return build_error_response(
            http_status=403,
            title="メッセージ詳細取得",
            detail="アクセスキーが無効です。",
            href=f"/inquiries/message_application/{message_id}"
        )

    # ② Lấy message từ DB mock
    msg: MockMessage | None = db.query(MockMessage).filter_by(message_id=message_id).first()
    if not msg:
        return build_error_response(
            http_status=400,
            title="メッセージ詳細取得",
            detail="メッセージを取得できませんでした。",
            href=f"/inquiries/message_application/{message_id}",
            errors=[{"code": "E0014", "message": "メッセージが存在しません。"}]
        )

    # ③ Đánh dấu đã đọc (trừ loại 3 / 2 / 6 như spec)
    if msg.message_type not in {"3", "2", "6"} and msg.is_new:
        msg.is_new = False
        db.commit()

    # ④ Xác định detail string
    detail_map = {
        "1": "通常のお知らせを取得しました。",
        "2": "不受理のお知らせを取得しました。",
        "3": "ファイル受領のお知らせを取得しました。",
        "4": "利用者識別番号等のお知らせを取得しました。",
        "5": "照会番号のお知らせを取得しました。",
        "6": "取下げ不可のお知らせを取得しました。",
        "8": "納付情報のお知らせを取得しました。"
    }
    detail_str = detail_map.get(msg.message_type, "メッセージ詳細を取得しました。")

    # ⑤ Build response 正常系 200
    body = {
        "metadata": {
            "title": "メッセージ詳細取得",
            "detail": detail_str,
            "access_key": f"{uuid.uuid4()}-0-01"
        },
        "_links": {
            "self":   {"href": f"/inquiries/message_application/{message_id}"},
            "parent": {"href": f"/inquiries/list_applications/{msg.reference_number}"},
            "document": {"href": f"/inquiries/document_application/{msg.document_id}"} if msg.document_id else None
        },
        "result": {
            "title": msg.title,
            "message_content": msg.content,
            "reference_number": msg.reference_number,
            "facility_name": "健康保険組合",
            "message_datetime": msg.datetime.isoformat(),
            "message_type": msg.message_type,
            "procedure_name": "資格取得届",
            "agency_number_name": "受付番号",
            "agency_number": "1234567890123456",
            "document_id": msg.document_id,
            "files": [{
                "file_name": "mock_document.pdf"
            }] if msg.document_id else [],
            "contact": None,
            "payment_info": None
        }
    }
    return JSONResponse(status_code=200, content=body)
