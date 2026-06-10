from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from app.database import get_db
from app.routers.auth import get_current_user
from app import models, schemas

router = APIRouter(tags=["Статьи и комментарии"])

#==== Статьи ====
@router.get("/", response_model=list[schemas.ArticleRead])
def get_articles(
    skip: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(20, ge=1, le=50, description="Лимит на страницу"),
    category: Optional[str] = Query(None, description="Фильтр: news, guide, discussion"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Article)
    if category:
        query = query.filter(models.Article.category == category)
        
    return query.order_by(models.Article.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{article_id}", response_model=schemas.ArticleRead)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.post("/", response_model=schemas.ArticleRead, status_code=status.HTTP_201_CREATED)
def create_article(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # author_id берётся из токена → защита от подмены
    db_article = models.Article(**article.model_dump(), author_id=current_user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.patch("/{article_id}", response_model=schemas.ArticleRead)
def update_article(
    article_id: int,
    update: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)
        
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")
        
    db.delete(article)
    db.commit()

#==== Комментарии ====
@router.get("/{article_id}/comments", response_model=list[schemas.CommentRead])
def get_comments(article_id: int, db: Session = Depends(get_db)):
    if not db.query(models.Article).filter(models.Article.id == article_id).first():
        raise HTTPException(status_code=404, detail="Статья не найдена")
        
    comments = (
        db.query(models.Comment)
        .options(joinedload(models.Comment.user))
        .filter(models.Comment.article_id == article_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )
    
    return [
        {
            "id": c.id,
            "article_id": c.article_id,
            "user_id": c.user_id,
            "text": c.text,
            "created_at": c.created_at,
            "author_name": c.user.name if c.user else "Удаленный пользователь",
            "author_avatar": c.user.avatar if c.user else None,
        }
        for c in comments
    ]


@router.post("/{article_id}/comments", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(
    article_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not db.query(models.Article).filter(models.Article.id == article_id).first():
        raise HTTPException(status_code=404, detail="Статья не найдена")
        
    db_comment = models.Comment(
        **comment.model_dump(), 
        article_id=article_id, 
        user_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {
        "id": db_comment.id,
        "article_id": db_comment.article_id,
        "user_id": db_comment.user_id,
        "text": db_comment.text,
        "created_at": db_comment.created_at,
        "author_name": current_user.name,
        "author_avatar": current_user.avatar,
    }

@router.patch("/comments/{comment_id}", response_model=schemas.CommentRead)
def edit_comment(
    comment_id: int,
    update: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    comment.text = update.text
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "article_id": comment.article_id,
        "user_id": comment.user_id,
        "text": comment.text,
        "created_at": comment.created_at,
        "author_name": current_user.name,
        "author_avatar": current_user.avatar,
    }


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на удаление")
        
    db.delete(comment)
    db.commit()