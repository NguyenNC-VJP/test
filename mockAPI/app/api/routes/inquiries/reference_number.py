# app/api/routes/inquiries/reference_number.py
"""
申請受付番号確認API (Mock)
-------------------------------------------------------
Spec : 別紙7 申請受付番号確認API仕様 1.64
Flow :
  1. Access-Key (A/B) check
  2. 仮受付番号(20桁) check
  3. polling count < 3  → 処理中
  4. polling count >=3 → 完了 & 受付番号(17桁)返却
"""

import uuid
from fastapi import APIRouter, Header, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.access_key_utils import is_valid_access_key
from app.utils.error_response_builder import build_error_response
from app.models.mock_reference_status import MockReferenceStatus

router = APIRouter(prefix="/inquiries", tags=["Inquiries - Reference Check"])

# ----------------------------------------------------------------------
@router.get("/reference_number")
def inquiry_reference_number(
    temporary_reference_number: str = Query(
        ...,
        min_length=20,
        max_length=20,
        description="仮受付番号 (20桁)"
    ),
    x_access_key: str = Header(..., alias="X-Access-Key"),
    db: Session = Depends(get_db)
):
    # ① Access-Key validation (A または B)
    if not is_valid_access_key(x_access_key):
        return build_error_response(
            http_status=403,
            title="申請受付番号確認",
            detail="アクセスキーが無効です。",
            href=f"/inquiries/reference_number/{temporary_reference_number}"
        )

    # ② 仮受付番号 format check
    if not temporary_reference_number.isdigit():
        return build_error_response(
            http_status=400,
            title="申請受付番号確認",
            detail="入力エラーが発生しました。",
            href=f"/inquiries/reference_number/{temporary_reference_number}",
            errors=[{
                "code": "E0002",
                "message": "仮受付番号は半角数字で設定してください。"
            }]
        )

    # ③ 取得 or 新規 Insert polling state
    rec = (
        db.query(MockReferenceStatus)
          .filter_by(reference_number=temporary_reference_number)
          .first()
    )
    if not rec:
        rec = MockReferenceStatus(
            reference_number=temporary_reference_number,
            poll_count=0
        )
        db.add(rec)
        db.commit()

    # ④ 増分 polling
    rec.poll_count += 1
    db.commit()

    # --------------------- build common parts --------------------------
    def _meta(detail: str):
        return {
            "title":  "申請受付番号確認",
            "detail": detail,
            "access_key": f"{uuid.uuid4()}-0-01"
        }

    self_href = f"/inquiries/reference_number/{temporary_reference_number}"

    # ⑤ poll_count < 3  → 処理中
    if rec.poll_count < 3:
        return JSONResponse(
            status_code=200,
            content={
                "metadata": _meta("申請データの受付処理を行っています。"),
                "_links": {"self": {"href": self_href}},
                "result": {
                    "reference_number": None,
                    "finished": False
                }
            }
        )

    # ⑥ 完了ケース
    return JSONResponse(
        status_code=200,
        content={
            "metadata": _meta("申請の受付が完了しました。"),
            "_links": {"self": {"href": self_href}},
            "result": {
                "reference_number": temporary_reference_number[:17],  # 受付番号
                "finished": True
            }
        }
    )
