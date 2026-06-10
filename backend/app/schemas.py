from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional


# === Пользователи ===
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# === Питомцы ===
class PetCreate(BaseModel):
    name: str
    type: str
    status: str
    description: str
    date: str
    city: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class PetRead(PetCreate):
    id: int
    owner_id: int
    
    class Config:
        from_attributes = True

class PetProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["dog", "cat", "other"]
    breed: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[str] = None  # YYYY-MM-DD
    color: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    is_chipped: Optional[bool] = False
    chip_number: Optional[str] = Field(None, max_length=50)

class PetProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[Literal["dog", "cat", "other"]] = None
    breed: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[str] = None
    color: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    is_chipped: Optional[bool] = None
    chip_number: Optional[str] = Field(None, max_length=50)

class PetProfileRead(PetProfileCreate):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# === Статьи ===
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)          # Markdown или HTML
    image_url: Optional[str] = None                   # Ссылка на обложку
    category: Optional[str] = Field(None, max_length=50) # "news", "guide", "discussion"


class ArticleRead(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None

# === Комментарии ===
class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class CommentRead(BaseModel):
    id: int
    article_id: int
    user_id: int
    text: str
    created_at: datetime
    author_name: str
    author_avatar: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)

# === Пропавшие питомцы ===
class PetForm(BaseModel):
    status: str
    name: Optional[str] = None
    type: str
    description: str
    date: str
    city: str
    image: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    contact_phone: Optional[str] = None
