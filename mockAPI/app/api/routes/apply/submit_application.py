# app/api/routes/apply/submit_application.py

import zipfile
import uuid
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.access_key_utils import is_valid_access_key_b
from app.utils.application_utils import generate_mock_application_data
from app.models.mock_reference_status  import MockReferenceStatus
from app.models.mock_application_status import MockApplicationStatus
from app.models.mock_message            import MockMessage
from app.models.mock_document           import MockDocument

router = APIRouter(prefix="/apply", tags=["申請データ送信"])
UPLOAD_DIR = "./mock_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

JST = timezone(timedelta(hours=9))

@router.post("/submit_application_set")
async def submit_application_set(
    id: str = Form(...),
    corporate_number: str = Form(...),
    oss_type: str = Form(...),
    remarks: str = Form(None),
    application_zip: UploadFile = File(...),
    x_access_key: str = Header(..., alias="X-Access-Key"),
    db: Session = Depends(get_db)
):
    """
    Mock 申請データ送信API
    ---------------------------------
    1. Validate access_key A
    2. Lưu file ZIP tạm
    3. Phát hành 仮受付番号 (20桁)
    4. Lưu MockReferenceStatus
    5. Random status_code (001/002/003/008)
    6. Nếu status_code in (003,008) → sinh MockDocument + MockMessage
    7. Lưu MockApplicationStatus
    8. Trả response đúng spec
    """

    # ① Validate access key
    if not is_valid_access_key_b(x_access_key):
        return JSONResponse(status_code=403, content={"detail": "アクセスキーが無効です。"})

    # ② Save ZIP file
    zip_filename = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(UPLOAD_DIR, zip_filename)
    with open(zip_path, "wb") as f_out:
        f_out.write(await application_zip.read())

    # ③ 仮受付番号
    temp_ref_no   = datetime.now().strftime("%Y%m%d%H%M%S%f")[:20]
    short_ref_no  = temp_ref_no[:17]

    # ④ Save reference state
    db.add(MockReferenceStatus(
        reference_number=temp_ref_no,
        poll_count=0,
        # original_filename=application_zip.filename
    ))

    # ⑤ Random status (pattern C)
    status_code = random.choice(["001", "002", "003", "008"])

    # ⑥ Optional: document & message (only for 003 / 008)
    messages = []
    if status_code == "003":                       # ← thay đổi tại đây
        sample_pdf = os.path.join(UPLOAD_DIR, "sample.pdf")
        if not os.path.exists(sample_pdf):
            with open(sample_pdf, "wb") as f_pdf:
                f_pdf.write(b"%PDF-1.4\n%mock sample\n")

        doc_id = str(uuid.uuid4())[:18]
        db.add(MockDocument(document_id=doc_id,
                            file_path=sample_pdf,
                            verify_sign="Valid"))

        msg_id = str(uuid.uuid4())[:18]
        db.add(MockMessage(
            message_id       = msg_id,
            reference_number = short_ref_no,
            message_type     = "3",
            title            = "ファイル受領のお知らせがあります",
            content          = "Mock file 受領メッセージです。",
            datetime         = datetime.now(JST),
            document_id      = doc_id,
            is_new           = True
        ))

        # d) add to messages list for ApplicationStatus
        messages.append({
        "message_id": msg_id,
        "message_type": "3",
        "new_arrivals": True,
        "datetime": datetime.now(JST).isoformat(),
        "title": "ファイル受領のお知らせがあります",
        "document_id": doc_id
    })

    # ⑦ Save MockApplicationStatus
    mock_data = generate_mock_application_data(short_ref_no)
    # override messages nếu có
    if messages:
        mock_data["messages"] = messages
    mock_app = MockApplicationStatus(**mock_data)
    db.add(mock_app)
    db.commit()  # flush toàn bộ

    # ⑧ Build response
    return JSONResponse(
        status_code=200,
        content={
            "metadata": {
                "title": "申請データ送信完了",
                "detail": "正常に申請データを受付けました。",
                "access_key": f"{uuid.uuid4()}-0-01"
            },
            "_links": {
                "self": {"href": "/apply/submit_application_set"}
            },
            "result": {
                "temporary_reference_number": temp_ref_no
            }
        }
    )

