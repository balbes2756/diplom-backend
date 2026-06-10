from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..services.storage import storage_service, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter(prefix="/uploads", tags=["Загрузка файлов"])


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Загрузка изображения в Bucket.ru.
    Возвращает публичный URL для сохранения в БД.
    """
    # Проверка расширения
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            detail=f"Недопустимый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        content = await file.read()

        # Проверка размера
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                400,
                detail=f"Файл слишком большой (максимум {MAX_FILE_SIZE // 1024 // 1024} МБ)",
            )

        # MIME-тип
        content_type = file.content_type or "image/jpeg"

        # Загрузка в Bucket
        image_url = storage_service.upload_image(
            file_content=content,
            original_filename=filename,
            content_type=content_type,
        )

        return {"url": image_url}

    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка загрузки: {str(e)}")