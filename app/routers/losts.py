from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas, database
from .auth import get_current_user_optional
from ..services.storage import storage_service
from ..services.clip_service import clip_service
from ..services.milvus_service import milvus_service
import requests

router = APIRouter(prefix="/losts", tags=["Объявления"])

@router.post("/", status_code=201)
def create_announcement(
    data: schemas.PetForm,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    """
    Создание объявления о пропаже/находке с ИИ-поиском совпадений.
    Только для авторизованных пользователей.
    """
    # 1. Создаём объявление в PostgreSQL
    new_ann = models.Pet(
        user_id=current_user.id if current_user else None,
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
    
    print(f"✅ Объявление создано: ID={new_ann.id}, user_id={current_user.id if current_user else 'аноним'}")

    # 2. Генерируем эмбеддинг через CLIP
    text = f"{new_ann.name} {new_ann.type} {new_ann.description}"
    image_bytes = None
    
    # Скачиваем изображение, если есть URL
    if new_ann.image:
        print(f"🖼️ Пытаемся скачать изображение: {new_ann.image}")
        try:
            response = requests.get(new_ann.image, timeout=5)
            if response.status_code == 200:
                image_bytes = response.content
                print(f"✅ Изображение скачано: {len(image_bytes)} байт")
            else:
                print(f"⚠️ Ошибка скачивания: статус {response.status_code}")
        except Exception as e:
            print(f"⚠️ Не удалось скачать изображение: {e}")

    # Генерируем комбинированный эмбеддинг
    embedding = clip_service.get_combined_embedding(text, image_bytes)
    print(f"✅ Эмбеддинг сгенерирован, размерность: {len(embedding)}")

    # 3. Сохраняем эмбеддинг в Milvus
    milvus_service.insert_embedding(
        pet_id=new_ann.id,
        embedding=embedding,
        status=new_ann.status,
        pet_type=new_ann.type
    )
    print(f"✅ Эмбеддинг сохранён в Milvus для pet_id={new_ann.id}")

    # 4. Если статус "found" — ищем совпадения среди "lost"
    matched_pets = []
    if new_ann.status == "found":
        matches = milvus_service.search_similar(
            query_embedding=embedding,
            status="lost",
            pet_type=new_ann.type,
            limit=5
        )
        
        # Получаем полные данные из PostgreSQL
        if matches:
            matched_ids = [m["pet_id"] for m in matches]
            matched_pets = db.query(models.Pet).filter(
                models.Pet.id.in_(matched_ids)
            ).all()
            print(f"✅ Найдено {len(matched_pets)} совпадений (БЕЗ ФИЛЬТРА)")
            for match in matches:
                pet = db.query(models.Pet).filter(models.Pet.id == match["pet_id"]).first()
                if pet:
                    name = pet.name if pet.name else "Без имени"
                    print(f"   - {name} ({pet.type}, {pet.status}): сходство {match['similarity']:.3f}")
        else:
            print("Совпадений не найдено")

    # 5. Возвращаем результат
    return {
        "id": new_ann.id,
        "user_id": new_ann.user_id,
        "name": new_ann.name,
        "type": new_ann.type,
        "status": new_ann.status,
        "description": new_ann.description,
        "date": new_ann.date,
        "city": new_ann.city,
        "lat": new_ann.lat,
        "long": new_ann.long,
        "image": new_ann.image,
        "contact_phone": new_ann.contact_phone,
        "created_at": str(new_ann.created_at),
        "is_active": new_ann.is_active,
        "matched_pets": [
            {
                "id": pet.id,
                "user_id": pet.user_id,
                "name": pet.name,
                "type": pet.type,
                "status": pet.status,
                "description": pet.description,
                "date": pet.date,
                "city": pet.city,
                "lat": pet.lat,
                "long": pet.long,
                "image": pet.image,
                "contact_phone": pet.contact_phone,
                "created_at": str(pet.created_at),
                "is_active": pet.is_active,
            }
            for pet in matched_pets
        ]
    }

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