"""
申請受付番号確認API (mock production-ready)
"""

from fastapi import APIRouter, Header, Query
from fastapi.responses import JSONResponse
from app.utils.access_key_utils import is_valid_access_key

router = APIRouter()

@router.get("/inquiries/reference_number")
async def inquiry_reference_number(
    reference_number: str = Query(...),                     # 照会対象の申請受付番号
    x_access_key: str = Header(None, alias="X-Access-Key")  # ヘッダーで受信するAccess-Key
):
    # Validate access_key format (only pattern check in mock)
    if not x_access_key or not is_valid_access_key(x_access_key):
        return JSONResponse(status_code=403, content={"detail": "アクセスキーが無効です。"})

    # Validate reference_number format (mock check)
    if not reference_number or len(reference_number) != 20:
        return JSONResponse(status_code=400, content={"detail": "受付番号の形式が不正です。"})

    # Always return accepted (mock always success)
    response = {
        "metadata": {
            "title": "申請受付番号確認",
            "detail": "受付け済みです。",
            "_links": {
                "self": {"href": "/inquiries/reference_number"}
            }
        },
        "result": {
            "application_status": "accepted"
        }
    }

    return response
