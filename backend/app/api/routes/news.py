from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app.schemas.news import News, NewsCreate, NewsUpdate
from app.services.news import get_news, get_news_by_id, create_news, update_news, delete_news
from app.deps import get_db, get_current_active_user
from app.models.user import User, UserRole

router = APIRouter(tags=["news"])  # убран prefix


# Получить список новостей
def is_admin_or_manager(user: User):
    if user.role not in [UserRole.admin, UserRole.manager]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user


@router.get("/", response_model=List[News])
def read_news(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return get_news(db, skip=skip, limit=limit)


@router.get(
    "/{news_id}",
    response_model=News,
    responses={404: {"description": "Новость не найдена"}},
)
def read_news_by_id(news_id: int, db: Session = Depends(get_db)):
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return db_news


# Только admin может создавать новости
@router.post("/", response_model=News, status_code=status.HTTP_201_CREATED)
def create_news_view(
    news: NewsCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # current_user — это SimpleNamespace, а не ORM-модель
    if getattr(current_user, "role", None) != UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    author_id = getattr(current_user, "id", None)
    if not isinstance(author_id, int):
        raise HTTPException(status_code=400, detail="Некорректный пользователь")
    return create_news(db, news, author_id=author_id)


@router.put("/{news_id}", response_model=News)
def update_news_view(
    news_id: int,
    news_update: NewsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    is_admin_or_manager(current_user)
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return update_news(db, db_news, news_update)


@router.delete(
    "/{news_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"description": "Новость не найдена"}},
)
def delete_news_view(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    is_admin_or_manager(current_user)
    db_news = get_news_by_id(db, news_id)
    if not db_news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    delete_news(db, db_news)
    return Response(status_code=204)
