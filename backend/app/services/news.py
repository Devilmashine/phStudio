from sqlalchemy.orm import Session
from ..models.news import News
from ..schemas.news import NewsCreate, NewsUpdate
from datetime import datetime
from typing import List, Optional

# CRUD-сервис для новостей


def get_news(db: Session, skip: int = 0, limit: int = 20) -> List[News]:
    return (
        db.query(News).order_by(News.created_at.desc()).offset(skip).limit(limit).all()
    )


def get_news_by_id(db: Session, news_id: int) -> Optional[News]:
    return db.query(News).filter(News.id == news_id).first()


def create_news(db: Session, news: NewsCreate, author_id: int) -> News:
    db_news = News(
        title=news.title,
        content=news.content,
        published=news.published,
        author_id=author_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def update_news(db: Session, db_news: News, news_update: NewsUpdate) -> News:
    db_news.title = news_update.title
    db_news.content = news_update.content
    db_news.published = news_update.published
    db_news.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_news)
    return db_news


def delete_news(db: Session, db_news: News) -> None:
    db.delete(db_news)
    db.commit()
