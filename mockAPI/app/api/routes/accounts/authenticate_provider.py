"""
民間サービス事業者認証 API (accounts/authenticate_provider)
"""

from fastapi import APIRouter, Form, Request, Depends
from sqlalchemy.orm import Session

# Import các module utils chuẩn hóa mock
from app.utils.error_response_builder import build_error_response
from app.utils.common_error_response import build_internal_server_error
from app.utils.database import get_db
from app.utils.access_key_utils import save_access_key

import uuid

# Khởi tạo router riêng cho API này
router = APIRouter()

@router.post("/accounts/authenticate_provider")
async def authenticate_provider_api(
    id: str = Form(...),                      # 民間サービス事業者ID (Provider ID)
    password: str = Form(...),                # 民間サービス事業者PW (Provider Secret)
    corporate_number: str = Form(...),        # 法人番号 (Corporate Number)
    redirect_url: str = Form(...),            # GビズID側 redirect URL (FE callback URL sau khi login)
    authentication_method: str = Form(...),   # 認証種別 (Auth Method: 固定値 "02")
    request: Request = None,
    db: Session = Depends(get_db)             # Inject DB session mock
):
    """
    API mock giả lập việc xác thực 民間サービス事業者 để phát hành access_key A
    """

    # Các giá trị dùng cho build response body (tái sử dụng nhiều lần)
    href = "/accounts/authenticate_provider"
    title = "民間サービス事業者認証"

    try:
        # ✅ Validate business logic mock (giả lập validate account fixed)
        if id != "test_provider_123" or password != "super_secret": 
            # Trường hợp 認証エラー → trả về HTTP 403 kèm lỗi chuẩn hóa
            return build_error_response(
                http_status=403,
                title=title,
                detail="認証エラーが発生しました。",
                href=href
            )

        # ✅ Sinh access_key A nếu login hợp lệ
        access_key_a = f"{uuid.uuid4()}-key1"

        # ✅ Insert access_key A vào mock DB stateful
        save_access_key(db, access_key_a, redirect_url)

        # ✅ Build response body mock chuẩn giống tài liệu production spec
        response = {
            "metadata": {
                "title": title,
                "detail": "正常発行されました。",
                "_links": {
                    "self": {
                        "href": href
                    }
                }
            },
            "result": {
                "access_key": access_key_a
            }
        }
        return response

    except Exception:
        # Nếu xảy ra lỗi hệ thống bất ngờ → trả về InternalServerError chuẩn hóa
        return build_internal_server_error(href=href, title=title)
