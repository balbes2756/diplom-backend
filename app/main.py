import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, pets, users, articles, uploads, losts

# Создаем таблицы в БД при запуске
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Хвост на время API")

# --- НАСТРОЙКА CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ os.getenv("FRONTEND_URL") ],  # ваш фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, tags=["auth"])
app.include_router(pets.router, tags=["pets"])
app.include_router(users.router, tags=["users"])
app.include_router(articles.router, prefix="/articles", tags=["articles"])
app.include_router(uploads.router)
app.include_router(losts.router)


@app.get("/")
def root():
    return {"message": "Backend is running 🐍", "docs": "/docs"}

