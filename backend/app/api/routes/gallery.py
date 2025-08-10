from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ...schemas.gallery import GalleryImage
from ...services.gallery import GalleryService
from ...core.database import get_db
from .auth import get_current_admin
from ...models.user import User
from typing import List
import os

UPLOAD_DIR = "backend/app/static/gallery/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("/", response_model=List[GalleryImage])
def get_gallery_images(db: Session = Depends(get_db)):
    service = GalleryService(db)
    return service.get_images()


@router.post("/upload", response_model=GalleryImage)
def upload_image(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Файл должен иметь имя")
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    url = f"/static/gallery/{filename}"
    service = GalleryService(db)
    return service.add_image(filename=filename, url=url, description=description)


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = GalleryService(db)
    if not service.delete_image(image_id):
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return {"status": "deleted"}
