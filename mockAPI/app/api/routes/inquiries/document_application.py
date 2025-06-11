# app/api/routes/inquiries/document_application.py
"""
公文書取得API (Mock)
-----------------------------------------
- URL:   /inquiries/document_application/{document_id}
- Method: GET
- Spec:  別紙11_公文書取得API仕様 1.64
"""

import base64
from pathlib import Path
import uuid
from fastapi import APIRouter, Path as FPath, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.access_key_utils import is_valid_access_key_b
from app.utils.error_response_builder import build_error_response
from app.models.mock_document import MockDocument

router = APIRouter()

@router.get("/inquiries/document_application/{document_id}")
def get_document(
    document_id: str = FPath(..., min_length=18, max_length=18),
    x_access_key: str = Header(..., alias="X-Access-Key"),
    db: Session = Depends(get_db)
):
    # ① Validate access key B
    if not is_valid_access_key_b(x_access_key):
        return build_error_response(
            http_status=403,
            title="公文書ダウンロード",
            detail="アクセスキーが無効です。",
            href=f"/inquiries/document_application/{document_id}"
        )

    # ② Lookup document
    doc: MockDocument | None = db.query(MockDocument).filter_by(document_id=document_id).first()
    if not doc:
        return build_error_response(
            http_status=400,
            title="公文書ダウンロード",
            detail="公文書を取得できませんでした。",
            href=f"/inquiries/document_application/{document_id}",
            errors=[{"code": "E0015", "message": "公文書が存在しません。"}]
        )

    # ③ Encode file to Base64
    data_b64 = ""
    try:
        with open(doc.file_path, "rb") as f:
            data_b64 = base64.b64encode(f.read()).decode()
    except IOError:
        return build_error_response(
            http_status=500,
            title="公文書ダウンロード",
            detail="Mock文書ファイルが読み込めません。",
            href=f"/inquiries/document_application/{document_id}"
        )

    # ④ Build 正常系 200
    body = {
        "metadata": {
            "title": "公文書ダウンロード",
            "detail": "公文書データを取得しました。",
            "access_key": f"{uuid.uuid4()}-0-01"
        },
        "_links": {
            "self":   {"href": f"/inquiries/document_application/{document_id}"},
            "parent": {"href": f"/inquiries/message_application/{document_id}"},
        },
        "resultset": {"count": 1},
        "results": [{
            "file_name": Path(doc.file_path).name,
            "file_content": data_b64,
            "verify_sign": doc.verify_sign,
            "eeCertificate": None,   # 省略 mock
            "caCertificates": []     # 省略 mock
        }]
    }
    return JSONResponse(status_code=200, content=body)
