from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class EmployeeBase(BaseModel):
    full_name: str = Field(..., example="Иван Иванов")
    position: str = Field(..., example="Менеджер")
    email: EmailStr
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    is_active: Optional[bool] = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeInDB(EmployeeBase):
    id: int

    class Config:
        from_attributes = True
