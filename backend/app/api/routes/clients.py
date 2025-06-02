from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.services.client import ClientService
from backend.app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from backend.app.models.user import User, UserRole
from backend.app.api.routes.auth import get_current_admin, get_current_manager

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=List[ClientResponse])
async def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_manager)):
    service = ClientService(db)
    return service.get_clients(skip=skip, limit=limit)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_manager)):
    service = ClientService(db)
    client = service.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@router.post("/", response_model=ClientResponse)
async def create_client(client_data: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = ClientService(db)
    return service.create_client(client_data)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client_data: ClientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = ClientService(db)
    client = service.update_client(client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@router.delete("/{client_id}")
async def delete_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = ClientService(db)
    ok = service.delete_client(client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return {"status": "success"}
