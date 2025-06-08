"""
申請データ送信API (Mock版)
"""

from fastapi import APIRouter, Form, UploadFile, File, Header
from fastapi.responses import JSONResponse
from app.utils.access_key_utils import is_valid_access_key
import uuid

# Khởi tạo router cho API 申請データ送信
router = APIRouter()

@router.post("/apply/submit_application_set")
async def submit_application_set(
    id: str = Form(...),                            # 民間サービス事業者ID (provider id)
    corporate_number: str = Form(...),              # 法人番号 (corporate number)
    oss_type: str = Form(...),                      # OSS種別 (oss type)
    remarks: str = Form(None),                      # 備考 (remarks - optional)
    application_zip: UploadFile = File(...),        # 申請ZIPファイル (upload file mock)
    x_access_key: str = Header(None, alias="X-Access-Key")  # ヘッダーからAccess-Keyを受け取る
):
    """
    API mock giả lập luồng gửi申請 dữ liệu (submit) như production spec.
    """

    # Validate access_key format (chỉ chấp nhận key B)
    if not x_access_key or not is_valid_access_key(x_access_key):
        return JSONResponse(status_code=403, content={"detail": "アクセスキーが無効です。"})

    # Sinh 仮受付番号 (reference_number) giống hệ thống production
    reference_number = "20240601" + str(uuid.uuid4().int)[0:12]

    # (Mock) Sinh access_key mới (key B) trả về sau khi submit thành công
    new_access_key = f"{uuid.uuid4()}-0-01"

    # Build response format theo đúng spec tài liệu chính thức
    response = {
        "metadata": {
            "title": "申請データ送信",
            "detail": "正常に受付けました。",
            "access_key": new_access_key
        },
        "_links": {
            "self": {
                "href": "/apply/submit_application_set"
            }
        },
        "result": {
            "temporary_reference_number": reference_number
        }
    }

    return response
