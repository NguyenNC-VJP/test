# app/api/routes/inquiries/reference_number.py

from fastapi import APIRouter, Header, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.utils.access_key_utils import is_valid_access_key
from app.utils.database import get_db
from app.models.mock_reference_status import MockReferenceStatus
import uuid

router = APIRouter()

@router.get("/inquiries/reference_number")
def inquiry_reference_number(
    reference_number: str = Query(...),
    x_access_key: str = Header(None, alias="X-Access-Key"),
    db: Session = Depends(get_db)
):
    # ① Validate access key
    if not x_access_key or not is_valid_access_key(x_access_key):
        return JSONResponse(status_code=403, content={"detail": "アクセスキーが無効です。"})

    # ② Validate reference number format
    if not reference_number or len(reference_number) != 20:
        return JSONResponse(status_code=400, content={"detail": "受付番号の形式が不正です。"})

    # ③ Tìm hoặc tạo mới trạng thái polling trong DB
    record = db.query(MockReferenceStatus).filter_by(reference_number=reference_number).first()
    if not record:
        record = MockReferenceStatus(reference_number=reference_number)
        db.add(record)
        db.commit()

    # ④ Cập nhật số lần polling
    record.poll_count += 1
    db.commit()

    # ⑤ Giả lập delay (chưa xử lý xong)
    if record.poll_count < 3:
        return JSONResponse(
            status_code=200,
            content={
                "metadata": {
                    "title": "申請受付番号確認",
                    "detail": "申請データの受付処理を行っています。",
                    "access_key": f"{uuid.uuid4()}-0-01"
                },
                "_links": {
                    "self": {"href": "/inquiries/reference_number"}
                },
                "result": {
                    "reference_number": None,
                    "finished": False
                }
            }
        )

    # ⑥ Khi đủ poll count thì xem là hoàn tất
    return JSONResponse(
        status_code=200,
        content={
            "metadata": {
                "title": "申請受付番号確認",
                "detail": "申請の受付が完了しました。",
                "access_key": f"{uuid.uuid4()}-0-01"
            },
            "_links": {
                "self": {"href": "/inquiries/reference_number"}
            },
            "result": {
                "reference_number": reference_number[:17],
                "finished": True
            }
        }
    )
