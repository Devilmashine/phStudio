from sqlalchemy.orm import Session
from app.models.employee_enhanced import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeService:
    @staticmethod
    def get_employee(db: Session, employee_id: int):
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_employees(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Employee).offset(skip).limit(limit).all()

    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate):
        db_employee = Employee(**employee.dict())
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
