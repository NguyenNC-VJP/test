from django.db import models

# accounts/models.py
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # thêm các trường tuỳ chỉnh nếu cần
    pass