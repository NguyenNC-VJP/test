# api/routes/submit_application.py

import re
from fastapi import APIRouter, Form, UploadFile, File, Header
from fastapi.responses import JSONResponse
from app.utils.access_key_utils import ACCESS_KEY_PATTERN_B, is_valid_access_key
import uuid

router = APIRouter()

@router.post("/apply/submit_application_set")
async def submit_application_set(
    id: str = Form(...),
    corporate_number: str = Form(...),
    oss_type: str = Form(...),
    remarks: str = Form(None),
    application_zip: UploadFile = File(...),
    x_access_key: str = Header(None, alias="X-Access-Key")
):
    # Validate B key (0-01)
    if not x_access_key or not re.match(ACCESS_KEY_PATTERN_B, x_access_key):
        return JSONResponse(status_code=403, content={"detail": "アクセスキーが無効です。"})

    reference_number = "20240601" + str(uuid.uuid4().int)[0:12]
    new_access_key = f"{uuid.uuid4()}-0-01"

    response = {
        "metadata": {
            "title": "申請データ送信",
            "detail": "正常に受付けました。",
            "access_key": new_access_key
        },
        "_links": {
            "self": {"href": "/apply/submit_application_set"}
        },
        "result": {
            "temporary_reference_number": reference_number
        }
    }
    return response
