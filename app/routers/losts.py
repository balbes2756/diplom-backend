from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .. import models, schemas, database
from .auth import get_current_user
from ..services.storage import storage_service

router = APIRouter(prefix="/losts", tags=["Объявления"])

@router.post("/", status_code=201)
def create_announcement(
    data: schemas.PetForm,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),  # ← Обязательная авторизация
):
    """
    Создание объявления о пропаже/находке.
    Только для авторизованных пользователей.
    """
    new_ann = models.Pet(
        user_id=current_user.id,  # ← Всегда заполнен
        name=data.name,
        type=data.type,
        status=data.status,
        description=data.description,
        date=data.date,
        city=data.city,
        lat=data.lat,
        long=data.lng,
        image=data.image,
        contact_phone=data.contact_phone,
    )
    
    db.add(new_ann)
    db.commit()
    db.refresh(new_ann)
    
    print(f"✅ Объявление создано: ID={new_ann.id}, user_id={current_user.id}")
    return new_ann

@router.get("/")
def get_announcements(
    status: Optional[str] = None,
    city: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(database.get_db),
):
    """
    Получение списка объявлений с фильтрацией.
    """
    query = db.query(models.Pet)
    
    if status:
        query = query.filter(models.Pet.status == status)
    if city:
        query = query.filter(models.Pet.city.ilike(f"%{city}%"))
    if type:
        query = query.filter(models.Pet.type == type)
    
    return query.order_by(models.Pet.created_at.desc()).all()

@router.get("/{announcement_id}")
def get_announcement(
    announcement_id: int,
    db: Session = Depends(database.get_db),
):
    """
    Получение одного объявления по ID.
    """
    announcement = db.query(models.Pet).filter(
        models.Pet.id == announcement_id,
        models.Pet.is_active == True
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    return announcement

@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Полное удаление объявления из БД и изображения из Bucket.ru.
    """
    # 1. Ищем объявление (без фильтра is_active — удаляем даже скрытые)
    announcement = db.query(models.Pet).filter(
        models.Pet.id == announcement_id
    ).first()

    if not announcement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # 2. Проверка авторства
    if announcement.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете удалить чужое объявление"
        )

    # 3. Удаляем изображение из Bucket.ru (если есть)
    if announcement.image:
        print(f"️ Удаляем изображение: {announcement.image}")
        try:
            storage_service.delete_image(announcement.image)
            print("✅ Файл удалён из хранилища")
        except Exception as e:
            print(f"⚠️ Не удалось удалить файл: {e}")

    # 4. Полное удаление из БД
    db.delete(announcement)
    db.commit()

    print(f"✅ Объявление #{announcement_id} полностью удалено")
    return {"message": "Объявление удалено"}