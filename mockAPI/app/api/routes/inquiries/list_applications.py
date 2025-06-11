# app/api/routes/inquiries/list_applications.py

import uuid
from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.application_utils import get_application_status
from app.utils.access_key_utils import is_valid_access_key_b
from app.utils.error_response_builder import build_error_response

router = APIRouter(
    prefix="/inquiries/list_applications",
    tags=["Inquiries - Application Status"]
)

@router.get("/{reference_number}")
async def get_application_detail(
    reference_number: str,
    x_access_key: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    モックAPI: 申請状況詳細取得API
    厚生労働省（健康保険組合）仕様パターンCに準拠

    - access_key（B）を検証
    - reference_number（17桁）を検証
    - mock DB から申請状況データを取得
    - 成功時: 申請詳細 + embedded messages（あれば）を返却
    """

    # ① Validate access key B
    if not is_valid_access_key_b(x_access_key):
        return build_error_response(
            http_status=403,
            title="申請状況詳細取得",
            detail="アクセスキーが無効です",
            href=f"/inquiries/list_applications/{reference_number}"
        )

    # ② Validate reference_number: 17 digits only
    if not (reference_number.isdigit() and len(reference_number) == 17):
        return build_error_response(
            http_status=400,
            title="申請状況詳細取得",
            detail="受付番号の形式が不正です",
            href=f"/inquiries/list_applications/{reference_number}",
            errors=[{
                "errorCode": "10003",
                "errorMessage": "受付番号は17桁の数字で入力してください"
            }]
        )

    try:
        # ③ Lấy dữ liệu mock từ DB (hoặc sinh mới nếu chưa có)
        app_status = get_application_status(db, reference_number)

        # ④ Build response
        response = {
            "metadata": {
                "title": "申請状況詳細取得",
                "detail": "申請状況詳細を取得しました。",
                "access_key": f"{uuid.uuid4()}-0-01"
            },
            "_links": {
                "self": {
                    "href": f"/inquiries/list_applications/{reference_number}"
                },
                "parent": {
                    "href": "/inquiries/list_application_sets"
                }
            },
            "result": {
                "reference_number": app_status.reference_number,
                "transmit_datetime": app_status.transmit_datetime.isoformat(),
                "corporate_name": app_status.corporate_name,
                "representative": app_status.representative,
                "_embedded": {
                    "procedures": app_status.procedures
                }
            }
        }

        # ⑤ Nếu có messages thì thêm vào `_embedded`
        if app_status.messages:
            response["result"]["_embedded"]["messages"] = [
                {
                    "message_id": msg["message_id"],
                    "message_type": msg["message_type"],
                    "new_arrivals": msg["new_arrivals"],
                    "datetime": msg["datetime"],
                    "title": msg["title"],
                    "document_id": msg.get("document_id"),
                    "_links": {
                        "self": {
                            "href": f"/inquiries/message_application/{msg['message_id']}"
                        },
                        "download": {
                            "href": f"/inquiries/document_application/{msg['document_id']}"
                        } if msg.get("document_id") else None
                    }
                }
                for msg in app_status.messages
            ]

        return JSONResponse(content=response)

    except Exception as e:
        # ⑥ Lỗi bất ngờ trong xử lý nội bộ
        return build_error_response(
            http_status=500,
            title="申請状況詳細取得",
            detail="サーバー内部エラーが発生しました。",
            href=f"/inquiries/list_applications/{reference_number}"
        )
