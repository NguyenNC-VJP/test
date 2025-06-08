"""
GビズID申請者認証 API (accounts/gbiz_id/authenticate_user)
"""

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

# Import các module utils chuẩn hóa mock
from app.utils.common_error_response import build_internal_server_error
from app.utils.access_key_utils import (
    is_valid_access_key_a,  # validate đúng theo spec access_key A
    get_redirect_url,
    delete_access_key,
    save_access_key
)
from app.utils.database import get_db
from app.utils.error_response_builder import build_gbizid_redirect_error
import uuid

# Khởi tạo router riêng cho API này
router = APIRouter()

@router.get("/gbizid/login")
async def issue_token(
    access_key: str = Query(...),  # access_key A từ frontend truyền lên
    request: Request = None,
    db: Session = Depends(get_db)
):
    href = "/gbizid/login"
    title = "申請者認証（GビズID）"

    try:
        # Case 1: access_key bắt buộc phải có
        if not access_key:
            return build_gbizid_redirect_error(None, "E0001", "アクセスキーが設定されていません。")

        # Case 2: access_key phải đúng định dạng access_key A
        if not is_valid_access_key_a(access_key):
            return build_gbizid_redirect_error(None, "E0006", "アクセスキーにコードを正しく設定してください。")

        # Case 3: lookup trong DB stateful mock xem access_key A còn tồn tại không
        redirect_url = get_redirect_url(db, access_key)
        if not redirect_url:
            return build_gbizid_redirect_error(None, "E0901", "認証エラーが発生しました。")

        # Nếu hợp lệ: tiến hành phát hành access_key B
        access_key_b = f"{uuid.uuid4()}-0-01"

        # Xóa access_key A cũ
        delete_access_key(db, access_key)

        # Lưu access_key B vào DB để phục vụ luồng callback sau đó
        save_access_key(db, access_key_b, redirect_url)

        # Redirect về frontend kèm access_key B
        redirect_with_param = (
            f"{redirect_url}"
            f"?title={title}"
            f"&detail=正常発行されました。"
            f"&self_href={href}"
            f"&access_key={access_key_b}"
        )
        return RedirectResponse(url=redirect_with_param, status_code=302)

    except Exception:
        # Nếu lỗi hệ thống bất ngờ → trả về InternalServerError theo mock chuẩn hóa
        return build_internal_server_error(href=href, title=title)
