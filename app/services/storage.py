import os
import uuid
from pathlib import Path
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# ===== Конфигурация из .env =====
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
REGION = os.getenv("S3_REGION", "ru-1")
ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
PUBLIC_URL = os.getenv("S3_PUBLIC_URL", "").rstrip("/")

# ===== Ограничения =====
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ


class BucketStorage:
    """Сервис для загрузки файлов в Bucket.ru (S3-совместимое хранилище)"""
    
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=REGION,
            endpoint_url=ENDPOINT_URL,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    
    def upload_image(
        self,
        file_content: bytes,
        original_filename: str,
        content_type: str,
    ) -> str:
        """
        Загружает изображение в Bucket.ru и возвращает публичный URL.
        
        Формат пути в хранилище: images/YYYY/MM/uuid.ext
        
        :raises ValueError: если файл не проходит валидацию
        :raises RuntimeError: если ошибка при загрузке в хранилище
        """
        # 1. Проверка размера
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(
                f"Файл слишком большой (максимум {MAX_FILE_SIZE // 1024 // 1024} МБ)"
            )
        
        # 2. Проверка MIME-типа
        if content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Недопустимый тип файла: {content_type}. "
                f"Разрешены: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        
        # 3. Проверка расширения
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Недопустимое расширение: {ext}. "
                f"Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 4. Генерация уникального пути: images/2026/06/abc123.jpg
        now = datetime.utcnow()
        folder = f"images/{now.year}/{now.month:02d}"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        s3_key = f"{folder}/{unique_name}"
        
        # 5. Загрузка в Bucket.ru
        # ACL не указываем — бакет уже публичный по умолчанию
        try:
            self.client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
            )
        except ClientError as e:
            raise RuntimeError(f"Ошибка загрузки в хранилище: {e}")
        
        # 6. Возвращаем публичный URL
        return f"{PUBLIC_URL}/{s3_key}"
    
    def delete_image(self, image_url: str) -> bool:
        """
        Удаляет изображение из Bucket.ru по его публичному URL.
        Возвращает True, если удаление прошло успешно.
        """
        if not image_url:
            print("⚠️ Пустой URL — нечего удалять")
            return False

        try:
            # Извлекаем ключ из URL
            # Вариант 1: URL начинается с PUBLIC_URL (самый частый случай)
            if image_url.startswith(PUBLIC_URL):
                s3_key = image_url.replace(f"{PUBLIC_URL}/", "", 1)
            else:
                # Вариант 2: URL с другим доменом — парсим через urlparse
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                s3_key = parsed.path.lstrip("/")
                # Если в пути есть название бакета — убираем его
                if s3_key.startswith(f"{BUCKET_NAME}/"):
                    s3_key = s3_key[len(BUCKET_NAME) + 1:]

            print(f"🗑️ Удаляю из Bucket.ru: bucket={BUCKET_NAME}, key={s3_key}")

            self.client.delete_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
            )

            print(f"✅ Файл успешно удалён из хранилища: {s3_key}")
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            print(f"❌ Ошибка S3 при удалении ({error_code}): {e}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка при удалении: {e}")
            return False


# Singleton-экземпляр для импорта в роутерах
storage_service = BucketStorage()