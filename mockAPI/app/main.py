"""
Entrypoint chính khởi động Mock Government API server
（Mock統合API起動エントリポイント）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import các module routing đã chuẩn hóa
from app.api.routes import (
    authenticate_provider,   # 民間サービス事業者認証 API
    gbizid_login,            # GビズID申請者認証 API
    submit_application,      # 申請データ送信 API
    inquiry_reference_number # 申請受付番号確認
)

# ========================
# Khởi tạo FastAPI App Instance
# ========================
app = FastAPI(
    title="Mock Government API",
    description="Mock for GビズID + Myna Portal (リダイレクト指定あり)",
    version="1.0"
)

# ========================
# Setup CORS Middleware (cho phép FE local call API dễ dàng)
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origin (dev mode)
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Đăng ký từng router vào hệ thống mock
# ========================
app.include_router(authenticate_provider.router)
app.include_router(gbizid_login.router)
app.include_router(submit_application.router)
app.include_router(inquiry_reference_number.router)
