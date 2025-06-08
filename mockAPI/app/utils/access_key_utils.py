"""
Utils quản lý access_key mock DB stateful
"""

import re
from sqlalchemy.orm import Session
from app.models.mock_access_keys import MockAccessKey

# Định nghĩa pattern access_key A (key1) và access_key B (key2) chuẩn spec mock
ACCESS_KEY_PATTERN_A = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-key1$"
ACCESS_KEY_PATTERN_B = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-0-01$"

def is_valid_access_key(access_key: str) -> bool:
    """
    Validate format access_key (chấp nhận cả A và B)
    """
    return bool(
        re.match(ACCESS_KEY_PATTERN_A, access_key)
        or re.match(ACCESS_KEY_PATTERN_B, access_key)
    )

def is_valid_access_key_a(access_key: str) -> bool:
    """
    Validate chỉ format access_key A (key1)
    """
    return bool(re.match(ACCESS_KEY_PATTERN_A, access_key))

def is_valid_access_key_b(access_key: str) -> bool:
    """
    Validate chỉ format access_key B (0-01)
    """
    return bool(re.match(ACCESS_KEY_PATTERN_B, access_key))

def save_access_key(db: Session, access_key: str, redirect_url: str):
    """
    Insert access_key mới vào DB mock
    """
    db_access_key = MockAccessKey(
        access_key=access_key,
        redirect_url=redirect_url
    )
    db.add(db_access_key)
    db.commit()

def get_redirect_url(db: Session, access_key: str) -> str:
    """
    Trả về redirect_url từ access_key mock nếu có
    """
    result = db.query(MockAccessKey).filter_by(access_key=access_key).first()
    return result.redirect_url if result else None

def delete_access_key(db: Session, access_key: str):
    """
    Xóa access_key sau khi phát hành access_key B
    """
    db.query(MockAccessKey).filter_by(access_key=access_key).delete()
    db.commit()
