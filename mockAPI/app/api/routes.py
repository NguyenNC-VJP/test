import os
import uuid
import re
from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()

# ========================== #
# Logic validate authenticate_provider (申請者認証)
# ========================== #

def validate_provider_input(id, password, corporate_number, redirect_url, authentication_method):
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

# Fake DB để giữ các access_key hợp lệ (cho authenticate_user kiểm tra)
valid_access_keys = set()

# ========================== #
# ① API authenticate_provider (申請者認証)
# ========================== #

@router.post("/accounts/authenticate_provider")
async def authenticate_provider(
    id: str = Form(...),
    password: str = Form(...),
    corporate_number: str = Form(...),
    redirect_url: str = Form(...),
    authentication_method: str = Form(...)
):
    # Validate đầu vào
    errors = validate_provider_input(id, password, corporate_number, redirect_url, authentication_method)
    if errors:
        return JSONResponse(status_code=400, content={
            "title": "民間サービス事業者認証",
            "detail": "入力エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": errors
        })

    # Validate ID/PW mock
    if id != "test_provider_123" or password != "super_secret":
        return JSONResponse(status_code=403, content={
            "title": "民間サービス事業者認証",
            "detail": "認証エラーが発生しました。",
            "_links": {"self": {"href": "/accounts/authenticate_provider"}},
            "errors": [{"code": "E0009", "message": "IDまたはパスワードが正しくありません。"}]
        })

    # Thành công → sinh access_key A và lưu vào mock DB
    access_key = str(uuid.uuid4()) + "-0-01"
    valid_access_keys.add(access_key)
    return {"access_key": access_key}


# ========================== #
# Logic validate authenticate_user (GビズID認証API)
# ========================== #

def is_valid_access_key_format(access_key: str) -> bool:
    pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-0-01$"
    return bool(re.match(pattern, access_key))

# Generate redirect error response (chuẩn spec)
def generate_redirect_error(error_code: str, error_message: str):
    error_redirect_url = (
        f"http://localhost:3000/gbizid/authenticate?"
        f"title=申請者認証（GビズID）"
        f"&error_code={error_code}"
        f"&error_message={error_message}"
        f"&self_href=%2Faccounts%2Fgbiz_id%2Fauthenticate_user"
    )
    return RedirectResponse(url=error_redirect_url)

# ========================== #
# ② API authenticate_user (GビズID認証API)
# ========================== #

@router.get("/accounts/gbiz_id/authenticate_user")
async def authenticate_user(
    access_key: str = Query(...),
    redirect_url: str = Query("http://localhost:3000/authenticate") 
):
    # Validate thiếu access_key (thực tế DRF xử lý trước nhưng ta vẫn theo tài liệu)
    if not access_key:
        return generate_redirect_error("E0001", "アクセスキーが設定されていません。")

    # Validate format access_key
    if not is_valid_access_key_format(access_key):
        return generate_redirect_error("E0006", "アクセスキーの形式が間違っています。")

    # Validate access_key có tồn tại trong mock DB
    if access_key not in valid_access_keys:
        return generate_redirect_error("E0901", "該当するアクセスキーレコードが存在しません。")

    # Thành công → sinh access_key B và redirect về frontend
    access_key_b = str(uuid.uuid4()) + "-mock"
    redirect_with_key = f"{redirect_url}?access_key={access_key_b}"
    return RedirectResponse(url=redirect_with_key)
