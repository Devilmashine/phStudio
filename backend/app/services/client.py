from sqlalchemy.orm import Session
from ..models.client import Client
from ..schemas.client import ClientCreate, ClientUpdate
from typing import List, Optional


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def get_client(self, client_id: int) -> Optional[Client]:
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_clients(self, skip: int = 0, limit: int = 100) -> List[Client]:
        return self.db.query(Client).offset(skip).limit(limit).all()

    def create_client(self, client_data: ClientCreate) -> Client:
        client = Client(**client_data.model_dump())
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update_client(
        self, client_id: int, client_data: ClientUpdate
    ) -> Optional[Client]:
        client = self.get_client(client_id)
        if not client:
            return None
        for field, value in client_data.model_dump(exclude_unset=True).items():
            setattr(client, field, value)
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete_client(self, client_id: int) -> bool:
        client = self.get_client(client_id)
        if not client:
            return False
        self.db.delete(client)
        self.db.commit()
        return True
