from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

# Импорт утилит и схем безопасности из корневого auth.py
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme  
)
from app import models, schemas
from app.database import get_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/auth", tags=["Auth"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не удалось проверить данные",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),  
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.email == email).first()
    return user


@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже занят")
    
    new_user = models.User(
        email=user.email,
        name=user.name,
        hashed_password=get_password_hash(user.password),
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user} 


@router.get("/me", response_model=schemas.UserRead)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user