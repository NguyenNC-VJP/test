from pathlib import Path
import os
#Đã fixed!
# =======================================================================================
# Xây dựng đường dẫn đến thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

# =======================================================================================
# Thiết lập nhanh cho môi trường phát triển - KHÔNG an toàn cho production!
# Tham khảo: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# Cảnh báo: KHÔNG để lộ secret key khi deploy production
SECRET_KEY = 'django-insecure-43_hjr6@ele0stdqcr&23^m4)7ehf8f8gc%^%p0&q*fg)$%5!z'

# Bật chế độ debug – chỉ dùng khi phát triển, KHÔNG nên bật ở production
DEBUG = True

# Danh sách các domain có thể truy cập website – để trống trong dev, nhưng cần cấu hình rõ ràng ở production
ALLOWED_HOSTS = []

# =======================================================================================
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',            # Giao diện admin mặc định của Django
    'django.contrib.auth',             # Hệ thống xác thực người dùng
    'django.contrib.contenttypes',     # Theo dõi các model được cài đặt
    'django.contrib.sessions',         # Hỗ trợ session (đăng nhập, giỏ hàng,...)
    'django.contrib.messages',         # Hệ thống hiển thị thông báo
    'django.contrib.staticfiles',      # Hỗ trợ quản lý static files (CSS, JS,...)
]
# =======================================================================================
# Middleware là các lớp xử lý request/response theo thứ tự
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',             # Bảo mật cơ bản
    'django.contrib.sessions.middleware.SessionMiddleware',      # Quản lý session
    'django.middleware.common.CommonMiddleware',                 # Middleware chung
    'django.middleware.csrf.CsrfViewMiddleware',                 # Bảo vệ CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # Gắn user vào request
    'django.contrib.messages.middleware.MessageMiddleware',      # Hỗ trợ thông báo
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    # Bảo vệ chống clickjacking
]
# =======================================================================================
# Trỏ đến file urls gốc của project
ROOT_URLCONF = 'mysite.urls'
# =======================================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # Dùng backend mặc định
        'DIRS': [],  # Nơi chứa các template tự định nghĩa (có thể thêm BASE_DIR / 'templates')
        'APP_DIRS': True,  # Tự động tìm template trong thư mục 'templates' của từng app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',  # Thêm đối tượng request vào context
                'django.contrib.auth.context_processors.auth',  # Thêm user & perms vào context
                'django.contrib.messages.context_processors.messages',  # Hỗ trợ hiển thị messages
            ],
        },
    },
]
# =======================================================================================
# Cấu hình cho WSGI – cổng kết nối giữa server và Django app
WSGI_APPLICATION = 'mysite.wsgi.application'
# =======================================================================================
# Cấu hình database (sử dụng SQLite3)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
# =======================================================================================
# Đọc các biến môi trường từ file .env để bảo mật thông tin kết nối database
from dotenv import load_dotenv
load_dotenv() # Tải các biến môi trường từ file .env
# Cấu hình database (sử dụng PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',   # Dùng PostgreSQL
        'NAME': os.getenv("DB_NAME"),                # Tên database
        'USER': os.getenv("DB_USER"),                # Tên user
        'PASSWORD': os.getenv("DB_PASSWORD"),        # Mật khẩu
        'HOST': os.getenv("DB_HOST"),                # Địa chỉ host (thường là localhost hoặc db container)
        'PORT': os.getenv("DB_PORT"),                # Cổng kết nối
    }
}
# =======================================================================================
# Cấu hình kiểm tra độ mạnh của mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {
        # Không cho mật khẩu giống thông tin cá nhân (username, email, v.v.)
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Yêu cầu mật khẩu đủ dài (mặc định tối thiểu 8 ký tự)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Không cho dùng mật khẩu phổ biến, dễ đoán (vd: "123456", "password")
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Không cho mật khẩu chỉ toàn số
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# =======================================================================================
# Thiết lập quốc tế hóa: ngôn ngữ và múi giờ mặc định
LANGUAGE_CODE = 'ja'                # Dùng tiếng Nhật cho giao diện mặc định
TIME_ZONE = 'Asia/Tokyo'           # Múi giờ chuẩn của Nhật Bản
USE_I18N = True                     # Bật dịch ngôn ngữ (internationalization)
USE_TZ = True                       # Bật sử dụng timezone-aware datetime
# =======================================================================================
# Là URL prefix dùng để trình duyệt truy cập các file tĩnh (CSS, JS, ảnh, fonts,...)
STATIC_URL = '/static/'
# =======================================================================================
# Kiểu trường id mặc định cho các model mới (BigAutoField = bigint, chống tràn số nếu bảng lớn)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# =======================================================================================