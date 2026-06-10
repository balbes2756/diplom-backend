from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite будет храниться в файле test.db
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/diplom"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,           # Проверяет соединение перед использованием
    connect_args={"connect_timeout": 3}  # ⏱️ Ждёт ответ БД не более 3 секунд
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()