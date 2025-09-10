from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from ...core.database import get_db
from ...models.employee_enhanced import Employee, EmployeeRole
from ...repositories.employee_repository import EmployeeRepository
from ...services.security_service import SecurityService
from ...core.event_bus import get_event_bus
from ...core.validation import EmployeeValidator
from ...core.errors import create_validation_error, create_not_found_error

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])

# Pydantic models for API
class EmployeeCreate(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    role: EmployeeRole
    phone: Optional[str] = None
    department: Optional[str] = None

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[EmployeeRole] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    username: str
    email: str
    role: EmployeeRole
    phone: Optional[str] = None
    department: Optional[str] = None
    status: str
    hire_date: Optional[str] = None
    created_at: str
    updated_at: str

class EmployeeListResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int

# Helper function to convert Employee model to response
def employee_to_response(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        username=employee.username,
        email=employee.email,
        role=employee.role,
        phone=employee.phone,
        department=employee.department,
        status=employee.status.value if employee.status else "active",
        hire_date=employee.hire_date.isoformat() if employee.hire_date else None,
        created_at=employee.created_at.isoformat() if employee.created_at else None,
        updated_at=employee.updated_at.isoformat() if employee.updated_at else None
    )

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee"""
    # Validate input
    validator = EmployeeValidator()
    validation_result = validator.validate_employee_data(employee_data.dict())
    
    if not validation_result.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": "Invalid employee data",
                "details": [error.__dict__ for error in validation_result.get_errors()]
            }
        )
    
    # Check if username or email already exists
    employee_repo = EmployeeRepository(db)
    if employee_repo.get_by_username(employee_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    if employee_repo.get_by_email(employee_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # Create employee
    try:
        # In a real implementation, we would hash the password
        # For now, we'll store it as-is (NOT recommended for production)
        employee = Employee(
            full_name=employee_data.full_name,
            username=employee_data.username,
            email=employee_data.email,
            password_hash=employee_data.password,  # In real implementation, hash this!
            role=employee_data.role,
            phone=employee_data.phone,
            department=employee_data.department,
            employee_id=f"EMP{employee_data.username.upper()}"  # Simple ID generation
        )
        
        # Save to database
        employee_repo = EmployeeRepository(db)
        created_employee = employee_repo.create(employee)
        
        logger.info(f"Created employee: {created_employee.username}")
        
        return employee_to_response(created_employee)
        
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create employee"
        )

@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    role: Optional[EmployeeRole] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List employees with filtering"""
    try:
        employee_repo = EmployeeRepository(db)
        
        # Build query based on filters
        if role:
            employees = employee_repo.get_by_role(role)
        elif status:
            # In a real implementation, we would filter by status
            employees = employee_repo.get_all(skip, limit)
        else:
            employees = employee_repo.get_all(skip, limit)
        
        # Apply pagination manually since our repository doesn't support filtering yet
        paginated_employees = employees[skip:skip+limit]
        
        employee_responses = [employee_to_response(emp) for emp in paginated_employees]
        
        return EmployeeListResponse(
            employees=employee_responses,
            total=len(employees)
        )
        
    except Exception as e:
        logger.error(f"Error listing employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list employees"
        )

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Get employee by ID"""
    try:
        employee_repo = EmployeeRepository(db)
        employee = employee_repo.get_by_id(employee_id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        return employee_to_response(employee)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get employee"
        )

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Update employee"""
    try:
        employee_repo = EmployeeRepository(db)
        employee = employee_repo.get_by_id(employee_id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Update fields
        update_data = employee_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(employee, field):
                setattr(employee, field, value)
        
        # Save changes
        updated_employee = employee_repo.update(employee)
        
        logger.info(f"Updated employee: {updated_employee.username}")
        
        return employee_to_response(updated_employee)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employee"
        )

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Delete employee"""
    try:
        employee_repo = EmployeeRepository(db)
        employee = employee_repo.get_by_id(employee_id)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Delete employee
        employee_repo.delete(employee)
        
        logger.info(f"Deleted employee ID: {employee_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee"
        )