"""
Error Response Builder (共通エラーレスポンスビルダー)
"""

from fastapi.responses import JSONResponse, RedirectResponse

def build_error_response(
    http_status: int,
    title: str,
    detail: str,
    href: str,
    errors: list = None
):
    """
    Build chuẩn unified error response dạng JSON theo common spec (dùng chung toàn hệ thống mock/prod)
    """
    response = {
        "title": title,                  # Tiêu đề lỗi (API module title)
        "detail": detail,                # Mô tả nội dung lỗi
        "_links": {
            "self": {
                "href": href             # API endpoint gây ra lỗi
            }
        }
    }

    # Nếu có danh sách lỗi chi tiết -> append vào response
    if errors:
        response["errors"] = errors

    return JSONResponse(status_code=http_status, content=response)


# ========================
# Chỉ dành cho GビズID申請者認証専用 redirect error (特殊仕様)
# ========================
def build_gbizid_redirect_error(redirect_url, error_code, error_message):
    """
    Build redirect error response theo spec gbizid authenticate_user API (bắt buộc redirect kèm error params)
    """
    if not redirect_url:
        redirect_url = "http://localhost:3000/error_page"  # fallback default khi thiếu redirect_url

    # Build redirect URL kèm query string chứa thông tin lỗi
    redirect_with_param = (
        f"{redirect_url}"
        f"?error_code={error_code}"
        f"&error_message={error_message}"
    )

    return RedirectResponse(url=redirect_with_param, status_code=302)
