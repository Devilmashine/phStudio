from sqlalchemy.orm import Session
from backend.app.models.gallery import GalleryImage
from backend.app.schemas.gallery import GalleryImageCreate
from typing import List
import os

class GalleryService:
    def __init__(self, db: Session):
        self.db = db

    def get_images(self) -> List[GalleryImage]:
        return self.db.query(GalleryImage).order_by(GalleryImage.uploaded_at.desc()).all()

    def add_image(self, filename: str, url: str, description: str = None) -> GalleryImage:
        image = GalleryImage(filename=filename, url=url, description=description or "")
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def delete_image(self, image_id: int) -> bool:
        image = self.db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
        if not image:
            return False
        self.db.delete(image)
        self.db.commit()
        # Физическое удаление файла (если хранится локально)
        url = getattr(image, "url", None)
        if isinstance(url, str) and url and os.path.exists(url):
            try:
                os.remove(url)
            except Exception:
                pass
        return True
