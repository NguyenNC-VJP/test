"""
Common error builder (System Internal Server Error 500 共通定義)
"""

def build_internal_server_error(href: str, title: str):
    """
    Build chuẩn unified response format cho system 500 error
    (áp dụng cho toàn bộ hệ thống khi có exception ngoài dự kiến)
    
    Parameters:
    - href: API endpoint gặp lỗi (dùng cho trace/debug dễ dàng)
    - title: API module title
    """
    return {
        "metadata": {
            "title": title,                          # API module title
            "detail": "Internal Server Error",       # Thông báo chung 500
            "_links": {
                "self": {"href": href}               # Ghi log chính xác URL gây lỗi
            }
        },
        "error": {
            "errorMessage": "Internal server unexpected error"  # Thông điệp chuẩn system error
        }
    }
