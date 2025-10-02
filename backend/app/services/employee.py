from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import uuid4

from app.models.employee_enhanced import Employee, EmployeeStatus
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

class EmployeeService:
    @staticmethod
    def get_employee(db: Session, employee_id: int):
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_employees(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Employee).offset(skip).limit(limit).all()

    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate):
        data = employee.dict()
        raw_password = data.pop("password")
        data["password_hash"] = pwd_context.hash(raw_password)
        data.setdefault("employee_id", f"EMP-{uuid4().hex[:6].upper()}")
        data.setdefault("status", EmployeeStatus.ACTIVE)

        db_employee = Employee(**data)
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate):
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if db_employee:
            for key, value in employee.dict(exclude_unset=True).items():
                setattr(db_employee, key, value)
            db.commit()
            db.refresh(db_employee)
        return db_employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int):
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if db_employee:
            db.delete(db_employee)
            db.commit()
        return db_employee
