from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeInDB
from app.services.employee import EmployeeService
from app.deps import get_db
from typing import List

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/", response_model=List[EmployeeInDB])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmployeeService.get_employees(db, skip=skip, limit=limit)

@router.get("/{employee_id}", response_model=EmployeeInDB)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/", response_model=EmployeeInDB)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return EmployeeService.create_employee(db, employee)

@router.put("/{employee_id}", response_model=EmployeeInDB)
def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = EmployeeService.update_employee(db, employee_id, employee)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}", response_model=EmployeeInDB)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = EmployeeService.delete_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee
