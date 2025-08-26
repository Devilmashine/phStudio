"""
Legal Document Management Service.
Handles versioning, publishing, and retrieval of legal documents.
"""

import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.legal_document import LegalDocument
from app.models.compliance_audit import ComplianceAuditLog


class LegalDocumentService:
    """Manages legal documents with versioning and audit trail"""
    
    DOCUMENT_TYPES = {
        "privacy_policy": "Политика обработки персональных данных",
        "terms_of_service": "Пользовательское соглашение (публичная оферта)",
        "cookie_policy": "Политика использования cookie",
        "public_offer": "Публичная оферта",
        "studio_rules": "Правила студии"
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(
        self,
        document_type: str,
        title: str,
        content: str,
        version: str,
        effective_date: datetime,
        created_by: Optional[int] = None
    ) -> LegalDocument:
        """Create a new version of a legal document"""
        
        if document_type not in self.DOCUMENT_TYPES:
            raise ValueError(f"Invalid document type. Must be one of: {list(self.DOCUMENT_TYPES.keys())}")
        
        # Generate content hash for integrity
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Deactivate previous versions
        self.db.query(LegalDocument).filter(
            and_(
                LegalDocument.document_type == document_type,
                LegalDocument.is_active == True
            )
        ).update({"is_active": False})
        
        # Create new document
        document = LegalDocument(
            document_type=document_type,
            version=version,
            title=title,
            content=content,
            published_date=datetime.now(timezone.utc),
            effective_date=effective_date,
            is_active=True,
            created_by=created_by,
            hash_signature=content_hash
        )
        
        self.db.add(document)
        
        # Create audit log
        audit_log = ComplianceAuditLog(
            event_type="LEGAL_DOCUMENT_PUBLISHED",
            user_identifier=f"admin_user_{created_by}" if created_by else "system",
            ip_address="127.0.0.1",  # System action
            action_details={
                "document_type": document_type,
                "version": version,
                "title": title,
                "effective_date": effective_date.isoformat(),
                "content_hash": content_hash
            }
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return document
    
    def get_active_document(self, document_type: str) -> Optional[LegalDocument]:
        """Get the currently active version of a document"""
        
        return self.db.query(LegalDocument).filter(
            and_(
                LegalDocument.document_type == document_type,
                LegalDocument.is_active == True,
                LegalDocument.effective_date <= datetime.now(timezone.utc)
            )
        ).first()
    
    def get_document_by_version(
        self,
        document_type: str,
        version: str
    ) -> Optional[LegalDocument]:
        """Get a specific version of a document"""
        
        return self.db.query(LegalDocument).filter(
            and_(
                LegalDocument.document_type == document_type,
                LegalDocument.version == version
            )
        ).first()
    
    def get_document_history(self, document_type: str) -> List[LegalDocument]:
        """Get all versions of a document, ordered by newest first"""
        
        return self.db.query(LegalDocument).filter(
            LegalDocument.document_type == document_type
        ).order_by(desc(LegalDocument.published_date)).all()
    
    def get_all_active_documents(self) -> Dict[str, LegalDocument]:
        """Get all currently active documents"""
        
        documents = self.db.query(LegalDocument).filter(
            and_(
                LegalDocument.is_active == True,
                LegalDocument.effective_date <= datetime.now(timezone.utc)
            )
        ).all()
        
        return {doc.document_type: doc for doc in documents}
    
    def verify_document_integrity(self, document_id: int) -> Dict[str, Any]:
        """Verify the integrity of a document using its hash"""
        
        document = self.db.query(LegalDocument).filter(
            LegalDocument.id == document_id
        ).first()
        
        if not document:
            return {"error": "Document not found"}
        
        # Recalculate hash
        current_hash = hashlib.sha256(document.content.encode('utf-8')).hexdigest()
        
        return {
            "document_id": document_id,
            "stored_hash": document.hash_signature,
            "calculated_hash": current_hash,
            "integrity_verified": current_hash == document.hash_signature
        }
    
    def search_documents(
        self,
        query: str,
        document_type: Optional[str] = None
    ) -> List[LegalDocument]:
        """Search documents by content or title"""
        
        search_query = self.db.query(LegalDocument).filter(
            LegalDocument.content.ilike(f"%{query}%") |
            LegalDocument.title.ilike(f"%{query}%")
        )
        
        if document_type:
            search_query = search_query.filter(
                LegalDocument.document_type == document_type
            )
        
        return search_query.order_by(desc(LegalDocument.published_date)).all()
    
    def get_document_versions_for_consent(self) -> Dict[str, str]:
        """Get current versions of all consent-related documents"""
        
        consent_doc_types = ["privacy_policy", "terms_of_service", "cookie_policy"]
        versions = {}
        
        for doc_type in consent_doc_types:
            doc = self.get_active_document(doc_type)
            if doc:
                versions[doc_type] = doc.version
            else:
                versions[doc_type] = "1.0"  # Default version
        
        return versions
    
    def create_default_documents(self) -> Dict[str, LegalDocument]:
        """Create default legal documents if they don't exist"""
        
        default_documents = {}
        
        # Privacy Policy
        if not self.get_active_document("privacy_policy"):
            privacy_content = """
# Политика обработки персональных данных

## 1. Общие положения

1.1. Настоящая Политика определяет порядок обработки и защиты персональных данных клиентов фотостудии.

1.2. Политика разработана в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ "О персональных данных".

## 2. Собираемые данные

2.1. Мы собираем следующие персональные данные:
- Имя
- Номер телефона
- Информация о бронированиях

## 3. Цели обработки

3.1. Персональные данные обрабатываются в целях:
- Оформления бронирования
- Связи с клиентом
- Информирования об услугах и акциях
- Улучшения качества обслуживания

## 4. Хранение и защита

4.1. Мы принимаем необходимые организационные и технические меры для защиты персональных данных.

4.2. Срок хранения персональных данных составляет 7 лет с момента последнего бронирования.

## 5. Права субъекта персональных данных

5.1. Вы имеете право:
- Получать информацию об обработке своих персональных данных
- Требовать уточнения или удаления своих персональных данных
- Отозвать согласие на обработку персональных данных
"""
            
            default_documents["privacy_policy"] = self.create_document(
                document_type="privacy_policy",
                title="Политика обработки персональных данных",
                content=privacy_content,
                version="1.0",
                effective_date=datetime.now(timezone.utc)
            )
        
        # Terms of Service
        if not self.get_active_document("terms_of_service"):
            terms_content = """
# Пользовательское соглашение (Публичная оферта)

## 1. Общие положения

1.1. Настоящее соглашение является публичной офертой для заключения договора на оказание услуг фотостудии.

1.2. Акцептом настоящей оферты является совершение действий по бронированию услуг.

## 2. Предмет договора

2.1. Исполнитель предоставляет Заказчику в аренду помещение фотостудии с оборудованием.

2.2. Срок аренды определяется при бронировании.

## 3. Права и обязанности сторон

3.1. Заказчик обязуется:
- Своевременно оплачивать услуги
- Бережно относиться к имуществу студии
- Соблюдать правила студии

3.2. Исполнитель обязуется:
- Предоставить помещение в состоянии, пригодном для использования
- Обеспечить работоспособность оборудования

## 4. Отмена бронирования

4.1. Отмена возможна не позднее 24 часов до начала аренды.

4.2. При отмене менее чем за 24 часа предоплата не возвращается.
"""
            
            default_documents["terms_of_service"] = self.create_document(
                document_type="terms_of_service",
                title="Пользовательское соглашение",
                content=terms_content,
                version="1.0",
                effective_date=datetime.now(timezone.utc)
            )
        
        # Cookie Policy
        if not self.get_active_document("cookie_policy"):
            cookie_content = """
# Политика использования файлов cookie

## 1. Что такое cookie

1.1. Cookie — это небольшие текстовые файлы, которые сохраняются на вашем устройстве при посещении сайта.

## 2. Типы используемых cookie

2.1. **Необходимые cookie** — обеспечивают базовую функциональность сайта

2.2. **Функциональные cookie** — запоминают ваши настройки и предпочтения

2.3. **Аналитические cookie** — помогают нам анализировать использование сайта

2.4. **Маркетинговые cookie** — используются для показа релевантной рекламы

## 3. Управление cookie

3.1. Вы можете в любое время изменить настройки cookie в вашем браузере.

3.2. Отключение cookie может повлиять на функциональность сайта.

## 4. Согласие

4.1. Продолжая использовать сайт, вы соглашаетесь с использованием cookie.
"""
            
            default_documents["cookie_policy"] = self.create_document(
                document_type="cookie_policy",
                title="Политика использования файлов cookie",
                content=cookie_content,
                version="1.0",
                effective_date=datetime.now(timezone.utc)
            )
        
        return default_documents