from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User

# Настройки
SECRET_KEY = "YAQilQq_niSESwZkvSy48O-Xr6j4wRImHbFPoKjexlc"  # ← Поменяй на случайную строку!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 схема (для получения токена из заголовков)
oauth2_scheme = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)