"""
Legal Document Management API Routes.
Handles legal document versioning, publishing, and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.services.legal_document_service import LegalDocumentService
from app.deps import get_current_admin, get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models
class LegalDocumentCreate(BaseModel):
    document_type: str = Field(..., description="Type of document (privacy_policy, terms_of_service, etc.)")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content in markdown")
    version: str = Field(..., description="Document version (e.g., 1.0, 2.1)")
    effective_date: datetime = Field(..., description="When document becomes effective")

class LegalDocumentResponse(BaseModel):
    id: int
    document_type: str
    title: str
    content: str
    version: str
    published_date: datetime
    effective_date: datetime
    is_active: bool
    created_by: Optional[int]
    hash_signature: Optional[str]

class DocumentVersionsResponse(BaseModel):
    privacy_policy: str
    terms_of_service: str
    cookie_policy: str

class DocumentIntegrityResponse(BaseModel):
    document_id: int
    stored_hash: Optional[str]
    calculated_hash: str
    integrity_verified: bool


@router.get("/documents/types")
async def get_document_types():
    """Get all available document types"""
    
    service = LegalDocumentService(None)  # No DB needed for this
    
    return {
        "document_types": service.DOCUMENT_TYPES,
        "available_types": list(service.DOCUMENT_TYPES.keys())
    }


@router.get("/documents/active")
async def get_all_active_documents(db: Session = Depends(get_db)):
    """Get all currently active legal documents"""
    
    service = LegalDocumentService(db)
    
    try:
        documents = service.get_all_active_documents()
        
        return {
            "documents": {
                doc_type: {
                    "id": doc.id,
                    "title": doc.title,
                    "version": doc.version,
                    "effective_date": doc.effective_date,
                    "published_date": doc.published_date
                }
                for doc_type, doc in documents.items()
            },
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active documents")


@router.get("/documents/{document_type}/current", response_model=LegalDocumentResponse)
async def get_current_document(
    document_type: str,
    db: Session = Depends(get_db)
):
    """Get the currently active version of a specific document type"""
    
    service = LegalDocumentService(db)
    
    if document_type not in service.DOCUMENT_TYPES:
        raise HTTPException(
            status_code=404, 
            detail=f"Document type '{document_type}' not found"
        )
    
    document = service.get_active_document(document_type)
    
    if not document:
        raise HTTPException(
            status_code=404, 
            detail=f"No active document found for type '{document_type}'"
        )
    
    return LegalDocumentResponse(
        id=document.id,
        document_type=document.document_type,
        title=document.title,
        content=document.content,
        version=document.version,
        published_date=document.published_date,
        effective_date=document.effective_date,
        is_active=document.is_active,
        created_by=document.created_by,
        hash_signature=document.hash_signature
    )


@router.get("/documents/{document_type}/version/{version}", response_model=LegalDocumentResponse)
async def get_document_by_version(
    document_type: str,
    version: str,
    db: Session = Depends(get_db)
):
    """Get a specific version of a document"""
    
    service = LegalDocumentService(db)
    
    document = service.get_document_by_version(document_type, version)
    
    if not document:
        raise HTTPException(
            status_code=404, 
            detail=f"Document '{document_type}' version '{version}' not found"
        )
    
    return LegalDocumentResponse(
        id=document.id,
        document_type=document.document_type,
        title=document.title,
        content=document.content,
        version=document.version,
        published_date=document.published_date,
        effective_date=document.effective_date,
        is_active=document.is_active,
        created_by=document.created_by,
        hash_signature=document.hash_signature
    )


@router.get("/documents/{document_type}/history")
async def get_document_history(
    document_type: str,
    db: Session = Depends(get_db)
):
    """Get version history for a document type"""
    
    service = LegalDocumentService(db)
    
    if document_type not in service.DOCUMENT_TYPES:
        raise HTTPException(
            status_code=404, 
            detail=f"Document type '{document_type}' not found"
        )
    
    documents = service.get_document_history(document_type)
    
    return {
        "document_type": document_type,
        "versions": [
            {
                "id": doc.id,
                "version": doc.version,
                "title": doc.title,
                "published_date": doc.published_date,
                "effective_date": doc.effective_date,
                "is_active": doc.is_active,
                "created_by": doc.created_by
            }
            for doc in documents
        ],
        "total_versions": len(documents)
    }


@router.post("/documents", response_model=LegalDocumentResponse)
async def create_document(
    document_data: LegalDocumentCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new version of a legal document (Admin only)"""
    
    service = LegalDocumentService(db)
    
    try:
        document = service.create_document(
            document_type=document_data.document_type,
            title=document_data.title,
            content=document_data.content,
            version=document_data.version,
            effective_date=document_data.effective_date,
            created_by=current_user.id
        )
        
        return LegalDocumentResponse(
            id=document.id,
            document_type=document.document_type,
            title=document.title,
            content=document.content,
            version=document.version,
            published_date=document.published_date,
            effective_date=document.effective_date,
            is_active=document.is_active,
            created_by=document.created_by,
            hash_signature=document.hash_signature
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")


@router.get("/documents/versions/current", response_model=DocumentVersionsResponse)
async def get_current_document_versions(db: Session = Depends(get_db)):
    """Get current versions of all consent-related documents"""
    
    service = LegalDocumentService(db)
    
    try:
        versions = service.get_document_versions_for_consent()
        return DocumentVersionsResponse(**versions)
        
    except Exception as e:
        logger.error(f"Failed to get document versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document versions")


@router.get("/documents/{document_id}/integrity", response_model=DocumentIntegrityResponse)
async def verify_document_integrity(
    document_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify the integrity of a document using its hash (Admin only)"""
    
    service = LegalDocumentService(db)
    
    try:
        result = service.verify_document_integrity(document_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return DocumentIntegrityResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify document integrity: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify document integrity")


@router.get("/documents/search")
async def search_documents(
    query: str,
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Search documents by content or title (Admin only)"""
    
    service = LegalDocumentService(db)
    
    try:
        documents = service.search_documents(query, document_type)
        
        return {
            "query": query,
            "document_type_filter": document_type,
            "results": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "title": doc.title,
                    "version": doc.version,
                    "published_date": doc.published_date,
                    "is_active": doc.is_active
                }
                for doc in documents
            ],
            "total_results": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to search documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to search documents")


@router.post("/documents/init-defaults")
async def initialize_default_documents(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Initialize default legal documents if they don't exist (Admin only)"""
    
    service = LegalDocumentService(db)
    
    try:
        documents = service.create_default_documents()
        
        return {
            "message": "Default documents initialized",
            "created_documents": list(documents.keys()),
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize default documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize default documents")


# Public endpoint for frontend to get document content
@router.get("/documents/public/{document_type}")
async def get_public_document(
    document_type: str,
    db: Session = Depends(get_db)
):
    """Get public document content for display on website"""
    
    service = LegalDocumentService(db)
    
    if document_type not in service.DOCUMENT_TYPES:
        raise HTTPException(
            status_code=404, 
            detail=f"Document type '{document_type}' not found"
        )
    
    document = service.get_active_document(document_type)
    
    if not document:
        raise HTTPException(
            status_code=404, 
            detail=f"No active document found for type '{document_type}'"
        )
    
    return {
        "document_type": document.document_type,
        "title": document.title,
        "content": document.content,
        "version": document.version,
        "effective_date": document.effective_date,
        "last_updated": document.published_date
    }