# app/api/routes.py
import os
import uuid
from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse

router = APIRouter()

# In-memory lưu access_key A đã phát sinh
issued_access_keys = {}

# Validate đầu vào authenticate_provider
def validate_input(id, password, corporate_number, redirect_url, authentication_method):
    errors = []
    if not id:
        errors.append({"code": "E0001", "message": "IDが設定されていません。"})
    if not password:
        errors.append({"code": "E0001", "message": "パスワードが設定されていません。"})
    if not corporate_number:
        errors.append({"code": "E0001", "message": "法人番号が設定されていません。"})
    elif len(corporate_number) != 13 or not corporate_number.isdigit():
        errors.append({"code": "E0003", "message": "法人番号は13桁の数字で設定してください。"})
    if not redirect_url:
        errors.append({"code": "E0001", "message": "リダイレクトURLが設定されていません。"})
    if authentication_method not in ["01", "02"]:
        errors.append({"code": "E0001", "message": "認証種別が不正です。"})
    return errors

# ① 民間サービス事業者認証API (申請者認証)
@router.post("/accounts/authenticate_provider")
async def authenticate_provider(
    id: str = Form(...),
    password: str = Form(...),
    corporate_number: str = Form(...),
    redirect_url: str = Form(...),
    authentication_method: str = Form(...)
):
    errors = validate_input(id, password, corporate_number, redirect_url, authentication_method)
    if errors:
        return JSONResponse(status_code=400, content={
            "title": "民間サービス事業者認証",
            "detail": "入力エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": errors
        })

    if id != "test_provider_123" or password != "super_secret":
        return JSONResponse(status_code=403, content={
            "title": "民間サービス事業者認証",
            "detail": "認証エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": [{"code": "E0009", "message": "IDまたはパスワードが正しくありません。"}]
        })

    access_key_a = str(uuid.uuid4()) + "-key1"
    # Lưu access_key A tạm
    issued_access_keys[access_key_a] = {
        "redirect_url": redirect_url
    }
    return {"access_key": access_key_a}

# ② GbizID Login画面 mock (申請者認証APIリダイレクト)
@router.get("/login_gbz")
async def login_gbizid(access_key: str = Query(...), redirect_url: str = Query(...)):
    if access_key not in issued_access_keys:
        return JSONResponse(status_code=400, content={
            "title": "GbizID認証",
            "detail": "不正なアクセスキーです。"
        })

    # Hiển thị màn hình login giả lập
    html_content = f"""
    <html><body>
    <h2>GビズIDログイン画面 (Mock)</h2>
    <p>access_key A: {access_key}</p>
    <form action="/gbizid/issue_token" method="post">
        <input type="hidden" name="access_key" value="{access_key}">
        <input type="hidden" name="redirect_url" value="{redirect_url}">
        <button type="submit">ログイン</button>
    </form>
    </body></html>
    """
    return HTMLResponse(content=html_content)

# ③ issue_token (申請者認証API応答)
@router.post("/gbizid/issue_token")
async def issue_token(access_key: str = Form(...), redirect_url: str = Form(...)):
    if access_key not in issued_access_keys:
        return JSONResponse(status_code=400, content={"error": "Invalid access_key"})

    # Sinh access_key B
    access_key_b = str(uuid.uuid4()) + "-key2"
    full_redirect = f"{redirect_url}?access_key={access_key_b}"

    # Xóa access_key A sau khi dùng (1 lần)
    issued_access_keys.pop(access_key)

    return RedirectResponse(url=full_redirect)
