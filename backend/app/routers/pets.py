from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.database import get_db
from app.routers.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/pets", tags=["pets"])

@router.post("/", response_model=schemas.PetRead)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # TODO: Здесь нужно получать owner_id из токена пользователя
    new_pet = models.Pet(**pet.dict(), owner_id=current_user.id)
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return new_pet

@router.get("/", response_model=list[schemas.PetRead])
def read_pets(db: Session = Depends(get_db)):
    pets = db.query(models.Pet).all()
    return pets

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    pet = db.query(models.Pet).filter(
        models.Pet.id == pet_id, 
        models.Pet.owner_id == current_user.id
    ).first()
    if not pet: raise HTTPException(404, "Не найден")
    db.delete(pet)
    db.commit()
    return {"ok": True}

# === ПРОФИЛИ ПИТОМЦЕВ ===

@router.post("/profile", response_model=schemas.PetProfileRead, status_code=status.HTTP_201_CREATED)
def create_pet_profile(
    pet_data: schemas.PetProfileCreate,  # ← Исправлено: двоеточие после pet_data
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Создать профиль питомца для текущего пользователя"""
    new_pet = models.PetProfile(
        **pet_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)
    return new_pet


@router.get("/profile/me", response_model=list[schemas.PetProfileRead])
def get_my_pet_profiles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Получить список профилей питомцев текущего пользователя"""
    return (
        db.query(models.PetProfile)
        .filter(models.PetProfile.owner_id == current_user.id)
        .order_by(models.PetProfile.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/profile/{pet_id}", response_model=schemas.PetProfileRead)
def get_pet_profile(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Получить профиль конкретного питомца (только своего)"""
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.owner_id == current_user.id
    ).first()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Профиль питомца не найден")
    
    return pet


@router.patch("/profile/{pet_id}", response_model=schemas.PetProfileRead)
def update_pet_profile(
    pet_id: int,
    update_data: schemas.PetProfileUpdate,  # ← Исправлено: двоеточие после update_data
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Обновить профиль питомца (только своего)"""
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.owner_id == current_user.id
    ).first()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Профиль питомца не найден")
    
    # Обновляем только переданные поля
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(pet, key, value)
    
    pet.updated_at = func.now()
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/profile/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_profile(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Удалить профиль питомца (только свой)"""
    pet = db.query(models.PetProfile).filter(
        models.PetProfile.id == pet_id,
        models.PetProfile.owner_id == current_user.id
    ).first()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Профиль питомца не найден")
    
    db.delete(pet)
    db.commit()
    # Возвращаем 204 No Content