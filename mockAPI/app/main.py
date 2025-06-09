"""
Entrypoint chính khởi động Mock Government API server
（Mock統合API起動エントリポイント）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import các module routing đã chuẩn hóa
from app.api.routes.accounts import authenticate_provider, gbizid_login
from app.api.routes.apply import submit_application
from app.api.routes.inquiries import reference_number 

from app.models.mock_access_keys import Base
from app.utils.database import engine



# ========================
# Khởi tạo FastAPI App Instance
# ========================
app = FastAPI(
    title="Mock Government API",
    description="Mock for GビズID + Myna Portal (リダイレクト指定あり)",
    version="1.0"
)

Base.metadata.create_all(bind=engine)
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
app.include_router(reference_number.router)
