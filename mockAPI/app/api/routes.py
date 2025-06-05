# app/api/routes.py

import os
import uuid
import re
from fastapi import  FastAPI,APIRouter,Request, Header, Form, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
#Hàm dùng chung.
def common_responses(api_title: str):
    return {
        400: {
            "description": "入力エラー",
            "content": {
                "application/json": {
                    "example": {
                        "title": api_title,
                        "detail": "入力エラーが発生しました。",
                        "_links": {"self": {"href": "API_PATH"}},
                        "errors": [{"code": "E0001", "message": "仮受付番号が設定されていません。"}]
                    }
                }
            }
        },
        403: {
            "description": "認証エラー",
            "content": {
                "application/json": {
                    "example": {
                        "title": api_title,
                        "detail": "アクセスキーが無効です。",
                        "_links": {"self": {"href": "API_PATH"}}
                    }
                }
            }
        },
        500: {
            "description": "サーバーエラー",
            "content": {
                "application/json": {
                    "example": {
                        "title": api_title,
                        "detail": "想定外のエラーが発生しました。",
                        "_links": {"self": {"href": "API_PATH"}}
                    }
                }
            }
        }
    }

# Khởi tạo router cho API (tất cả endpoint của mock API sẽ đi qua router này)
router = APIRouter()

# ========================== #
# Logic validate authenticate_provider (申請者認証)-1
# ========================== #

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

# Fake DB để giữ các access_key hợp lệ (cho authenticate_user kiểm tra)
valid_access_keys = set()

# ========================== #
# ① API authenticate_provider (申請者認証)
# ========================== #

@router.post("/accounts/authenticate_provider",responses=common_responses("申請データ送信"))
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

# ========================== #
# Logic validate authenticate_user (GビズID認証API)-2
# ========================== #

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

@router.get("/accounts/gbiz_id/authenticate_user",responses=common_responses("申請データ送信"))
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

#====================================================================================================================== #
    # # Logic 送信ー３
    # # ====================================================================================================================== #
    # router = APIRouter()

    # # Giả lập kho access_key
    # valid_access_keys = {"mock-access-key-1234567890-0-01"}

    # # Hàm kiểm tra định dạng access_key
    # def is_valid_access_key_format(access_key: str) -> bool:
    #     pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-0-01$"
    #     return bool(re.match(pattern, access_key))

    # # ========================== #
    # ## ===== API gửi hồ sơ申請送信（統一入力フォーム形式） ===== #
    # # ========================== #
    # @router.post("/apply/submit_application_set")
    # async def submit_application_set(
    #     id: str = Form(...),  # Đây chính là access_key B
    #     corporate_number: str = Form(...),
    #     form_type: str = Form(...),
    #     oss_type: str = Form(...),
    #     remarks: str = Form(None),
    #     application_zip: UploadFile = File(...)
    # ):
    #     # ✅ 1. Kiểm tra định dạng access_key
    #     if not is_valid_access_key_format(id):
    #         return JSONResponse(status_code=400, content={
    #             "result": "NG",
    #             "code": "E0006",
    #             "message": "アクセスキーの形式が間違っています。",
    #             "error_detail": "access_keyの形式はUUID-0-01である必要があります。"
    #         })
    #     # ✅ 2. Kiểm tra access_key tồn tại
    #     if id not in valid_access_keys:
    #         return JSONResponse(status_code=401, content={
    #             "result": "NG",
    #             "code": "E0901",
    #             "message": "認証に失敗しました。",
    #             "error_detail": "指定されたaccess_keyは無効です。"
    #         })

    #     # ✅ 3. Kiểm tra mã công ty
    #     if len(corporate_number) != 13 or not corporate_number.isdigit():
    #         return JSONResponse(status_code=400, content={
    #             "result": "NG",
    #             "code": "E0003",
    #             "message": "法人番号は13桁の数字で設定してください。",
    #             "error_detail": "corporate_numberが不正です。"
    #         })

    #     # ✅ 4. Kiểm tra file .zip
    #     if not application_zip.filename.endswith(".zip"):
    #         return JSONResponse(status_code=400, content={
    #             "result": "NG",
    #             "code": "E0004",
    #             "message": "ZIPファイルをアップロードしてください。",
    #             "error_detail": f"不正なファイル形式: {application_zip.filename}"
    #         })

    #     # ✅ 5. Nếu hợp lệ, sinh access_key mới + reference_number
    #     new_access_key = str(uuid.uuid4()) + "-0-01"
    #     valid_access_keys.add(new_access_key)

    #     temporary_reference_number = "20240601" + str(uuid.uuid4().int)[0:12]

    #     return{
    #   "metadata": {
    #     "title": "申請データ送信",
    #     "detail": "正常に受け付けました。"
    #   },
    #   "access_key": "abcde-...-0-01",
    #   "_links": {
    #     "self": {
    #       "href": "/apply/submit_application_set"
    #     },
    #     "reference": {
    #       "href": "/inquiries/reference_number/20240601987654321012"
    #     }
    #   },
    #   "result": {
    #     "temporary_reference_number": "20240601987654321012"
    #   }
    # }
    
#ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー



# Giả lập kho access_key
valid_access_keys = {"mock-access-key-1234567890-0-01"}

# Hàm kiểm tra định dạng access_key
def is_valid_access_key_format(access_key: str) -> bool:
    pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-0-01$"
    return bool(re.match(pattern, access_key))

# Hàm tạo phản hồi lỗi chuẩn tài liệu
def make_error_response(status_code: int, code: str = None, message: str = None):
    content = {
        "title": "申請データ送信",
        "detail": (
            "アクセスキーが無効です。" if status_code == 403 else
            "入力エラーが発生しました。" if status_code == 400 else
            "想定外のエラーが発生しました。"
        ),
        "_links": {
            "self": {
                "href": "/apply/submit_application_set"
            }
        }
    }
    if code and message:
        content["errors"] = [{"code": code, "message": message}]
    return JSONResponse(status_code=status_code, content=content)

@router.post("/apply/submit_application_set",responses=common_responses("申請データ送信"))
async def submit_application_set(
    id: str = Form(...),  # access_key
    corporate_number: str = Form(...),
    form_type: str = Form(...),
    oss_type: str = Form(...),
    remarks: str = Form(None),
    application_zip: UploadFile = File(...)
):
    # 1. access_key định dạng sai
    if not is_valid_access_key_format(id):
        return make_error_response(400, "E0006", "アクセスキーの形式が間違っています。")

    # 2. access_key không hợp lệ
    if id not in valid_access_keys:
        return make_error_response(403)

    # 3. mã công ty sai
    if len(corporate_number) != 13 or not corporate_number.isdigit():
        return make_error_response(400, "E0003", "法人番号は13桁の数字で設定してください。")

    # 4. file không đúng .zip
    if not application_zip.filename.endswith(".zip"):
        return make_error_response(400, "E0001", "申請ZIPファイルが設定されていません。")

    # ✅ Nếu hợp lệ
    new_access_key = str(uuid.uuid4()) + "-0-01"
    valid_access_keys.add(new_access_key)
    reference_number = "20240601" + str(uuid.uuid4().int)[0:12]

    return {
        "metadata": {
            "title": "申請データ送信",
            "detail": "正常に受け付けました。"
        },
        "access_key": new_access_key,
        "_links": {
            "self": {
                "href": "/apply/submit_application_set"
            },
            "reference": {
                "href": f"/inquiries/reference_number/{reference_number}"
            }
        },
        "result": {
            "temporary_reference_number": reference_number
        }
    }

#-----------------------------------------------
#-                                              -
#-------------------------------------------------

# === Khởi tạo app và middleware ===
app = FastAPI(title="Mock API - 申請受付番号確認", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Khởi tạo router ===


# === Access key hợp lệ (mock) ===
valid_access_keys = {"mock-access-key-1234567890-0-01"}

# === 仮受付番号 mẫu (mock dữ liệu) ===
mock_submissions = {
    "20240601abcdef123456": {
        "status": "completed",
        "reference_number": "2024060100012345678",
    },
    "20240601processing9999": {
        "status": "processing"
    },
    "20240601inputerror8888": {
        "status": "input_error",
        "errors": [
            {"code": "E0002", "message": "仮受付番号は半角数字20桁で設定してください。"}
        ]
    }
}

# === Kiểm tra định dạng access_key ===
def is_valid_access_key_format(access_key: str) -> bool:
    pattern = r"^[a-f0-9\-]{36}-0-01$"
    return re.match(pattern, access_key) is not None

# === API: 確認受付番号 ===
@router.get("/inquiries/reference_number",responses=common_responses("申請データ送信"))
async def check_reference_number(
    temporary_reference_number: str = Query(None, min_length=1),
    x_access_key: str = Header(None, alias="X-Access-Key"),
    request: Request = None
):
    url = str(request.url)

    # 1. Kiểm tra access_key
    if not x_access_key or not is_valid_access_key_format(x_access_key) or x_access_key not in valid_access_keys:
        return JSONResponse(
            status_code=403,
            content={
                "title": "申請受付番号確認",
                "detail": "アクセスキーが無効です。",
                "_links": {"self": {"href": url}}
            }
        )

    # 2. Kiểm tra 仮受付番号
    if not temporary_reference_number:
        return JSONResponse(
            status_code=400,
            content={
                "title": "申請受付番号確認",
                "detail": "入力エラーが発生しました。",
                "_links": {"self": {"href": url}},
                "errors": [{"code": "E0001", "message": "仮受付番号が設定されていません。"}]
            }
        )

    # 3. Sinh access_key mới
    new_access_key = str(uuid.uuid4()) + "-0-01"
    valid_access_keys.add(new_access_key)

    data = mock_submissions.get(temporary_reference_number)

    # 4. Không tìm thấy
    if data is None:
        return JSONResponse(
            status_code=400,
            content={
                "title": "申請受付番号確認",
                "detail": "申請情報を取得できませんでした。",
                "_links": {"self": {"href": url}},
                "errors": [{"code": "E0010", "message": "申請情報が存在しません。"}]
            }
        )

    # 5. Trường hợp hoàn tất
    if data["status"] == "completed":
        return {
            "metadata": {
                "title": "申請受付番号確認",
                "detail": "申請の受付が完了しました。",
                "access_key": new_access_key
            },
            "_links": {"self": {"href": url}},
            "result": {
                "reference_number": data["reference_number"],
                "finished": True
            }
        }

    # 6. Đang xử lý
    if data["status"] == "processing":
        return {
            "metadata": {
                "title": "申請受付番号確認",
                "detail": "申請データの受付処理を行っています。",
                "access_key": new_access_key
            },
            "_links": {"self": {"href": url}},
            "result": {
                "reference_number": None,
                "finished": False
            }
        }

    # 7. Lỗi nhập liệu
    if data["status"] == "input_error":
        return {
            "metadata": {
                "title": "申請受付番号確認",
                "detail": "申請を受け付けできませんでした。入力エラーを解消してください。",
                "access_key": new_access_key
            },
            "_links": {"self": {"href": url}},
            "result": {
                "reference_number": None,
                "finished": False
            },
            "errors": data["errors"]
        }

    # 8. Lỗi không mong muốn
    return JSONResponse(
        status_code=500,
        content={
            "title": "申請受付番号確認",
            "detail": "想定外のエラーが発生しました。",
            "_links": {"self": {"href": url}}
        }
    )

# === Đăng ký router vào app ===
app.include_router(router)
