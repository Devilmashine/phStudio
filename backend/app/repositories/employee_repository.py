from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
from .base_repository import BaseRepository

class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee entities"""
    
    def __init__(self, db: Session):
        from ..models.employee_enhanced import Employee
        super().__init__(db, Employee)
    
    def get_by_username(self, username: str) -> Optional[Employee]:
        """Get employee by username"""
        return self.db.query(self.model).filter(self.model.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return self.db.query(self.model).filter(self.model.email == email).first()
    
    def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by employee_id"""
        return self.db.query(self.model).filter(self.model.employee_id == employee_id).first()
    
    def get_by_role(self, role: EmployeeRole) -> List[Employee]:
        """Get employees by role"""
        return self.db.query(self.model).filter(self.model.role == role).all()
    
    def get_active_employees(self) -> List[Employee]:
        """Get all active employees"""
        return self.db.query(self.model).filter(self.model.status == EmployeeStatus.ACTIVE).all()
    
    def get_employees_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """Get employees by status"""
        return self.db.query(self.model).filter(self.model.status == status).all()