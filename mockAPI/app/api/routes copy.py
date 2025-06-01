# app/api/routes.py

import os
import uuid
from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse

# Khởi tạo router cho API (tất cả endpoint của mock API sẽ đi qua router này)
router = APIRouter()

# Biến toàn cục (in-memory) tạm thời để lưu các access_key A đã phát sinh
# Chỉ phục vụ cho mục đích mock - không lưu DB
issued_access_keys = {}

# ----------------------------------------
# Hàm validate đầu vào cho API authenticate_provider
# Kiểm tra các trường yêu cầu có hợp lệ không theo tài liệu chuẩn仕様書
# ----------------------------------------
def validate_input(id, password, corporate_number, redirect_url, authentication_method):
    errors = []
    
    # Kiểm tra ID có được nhập không
    if not id:
        errors.append({"code": "E0001", "message": "IDが設定されていません。"})
    
    # Kiểm tra password có được nhập không
    if not password:
        errors.append({"code": "E0001", "message": "パスワードが設定されていません。"})

    # Kiểm tra corporate_number: bắt buộc 13 ký tự số
    if not corporate_number:
        errors.append({"code": "E0001", "message": "法人番号が設定されていません。"})
    elif len(corporate_number) != 13 or not corporate_number.isdigit():
        errors.append({"code": "E0003", "message": "法人番号は13桁の数字で設定してください。"})

    # Kiểm tra redirect_url có được nhập không
    if not redirect_url:
        errors.append({"code": "E0001", "message": "リダイレクトURLが設定されていません。"})

    # Kiểm tra authentication_method có hợp lệ không (chỉ chấp nhận 01 hoặc 02)
    if authentication_method not in ["01", "02"]:
        errors.append({"code": "E0001", "message": "認証種別が不正です。"})

    return errors

# =====================================================
# ① 民間サービス事業者認証API (申請者認証)
# API được BE gọi đầu tiên sau khi user login nội bộ
# Gửi thông tin provider → Sinh access_key A → trả về cho BE
# =====================================================
@router.post("/accounts/authenticate_provider")
async def authenticate_provider(
    id: str = Form(...),
    password: str = Form(...),
    corporate_number: str = Form(...),
    redirect_url: str = Form(...),
    authentication_method: str = Form(...)
):
    # Bước 1: Validate dữ liệu đầu vào (giống tài liệu chính thức)
    errors = validate_input(id, password, corporate_number, redirect_url, authentication_method)
    if errors:
        return JSONResponse(status_code=400, content={
            "title": "民間サービス事業者認証",
            "detail": "入力エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": errors
        })

    # Bước 2: Kiểm tra ID/PW (giả lập xác thực nội bộ)
    if id != "test_provider_123" or password != "super_secret":
        return JSONResponse(status_code=403, content={
            "title": "民間サービス事業者認証",
            "detail": "認証エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": [{"code": "E0009", "message": "IDまたはパスワードが正しくありません。"}]
        })

    # Bước 3: Sinh access_key A (tạm gắn hậu tố key1 để phân biệt)
    access_key_a = str(uuid.uuid4()) + "-key1"

    # Bước 4: Lưu access_key A tạm vào bộ nhớ RAM (sử dụng cho luồng tiếp theo)
    issued_access_keys[access_key_a] = {
        "redirect_url": redirect_url  # redirect_url gốc từ client gửi lên
    }

    # Bước 5: Trả về access_key A cho BE
    return {"access_key": access_key_a}

# =====================================================
# ② GbizID Login画面 mock (申請者認証APIリダイレクト)
# BE redirect user FE đến mock login GbizID → user xác nhận đăng nhập tại đây
# =====================================================
@router.get("/login_gbz")
async def login_gbizid(access_key: str = Query(...)):
    # Check access_key hợp lệ
    if access_key not in issued_access_keys:
        return JSONResponse(status_code=400, content={"detail": "不正なアクセスキーです。"})

    html_content = f"""
    <html><body>
    <h2>GビズIDログイン画面 (Mock)</h2>
    <p>access_key A: {access_key}</p>
    <form action="/gbizid/login" method="post">
        <input type="hidden" name="access_key" value="{access_key}">
        <button type="submit">ログイン</button>
    </form>
    </body></html>
    """
    return HTMLResponse(content=html_content)

    # Thay vì hiển thị HTML, redirect sang UI React FE đã dựng sẵn
    # fe_login_mock_url = f"http://localhost:3000/issue_token?access_key={access_key}"
    # return RedirectResponse(url=fe_login_mock_url)

# =====================================================
# ③ issue_token (申請者認証API応答)
# Người dùng nhấn ログイン → sinh access_key B → redirect về lại FE (redirect_url)
# =====================================================
@router.post("/gbizid/login")
async def issue_token(access_key: str = Form(...)):
    if access_key not in issued_access_keys:
        return JSONResponse(status_code=400, content={"error": "Invalid access_key"})

    # Sinh access_key B
    access_key_b = str(uuid.uuid4()) + "-key2"

    # Lấy redirect_url đã lưu từ khi authenticate_provider
    redirect_url = issued_access_keys[access_key]["redirect_url"]

    # Build URL trả về chuẩn 302 như tài liệu
    redirect_with_param = (
        f"{redirect_url}"
        f"?title=申請者認証（GビズID）"
        f"&detail=正常発行されました。"
        f"&self_href=%2Faccounts%2Fgbiz_id%2Fauthenticate_user"
        f"&access_key={access_key_b}"
    )

    issued_access_keys.pop(access_key)
    return RedirectResponse(url=redirect_with_param, status_code=302)


