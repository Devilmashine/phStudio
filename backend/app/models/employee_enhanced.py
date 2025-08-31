from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from .enhanced_base import EnhancedBase as Base
from .base_enhanced import EnhancedBase

class EmployeeRole(str, enum.Enum):
    OWNER = "owner"      # Full system access
    ADMIN = "admin"      # Administrative access
    MANAGER = "manager"  # Operational access

class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class Employee(Base, EnhancedBase):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), unique=True, nullable=False)  # Internal ID
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(EmployeeRole), nullable=False)
    
    # Enhanced security fields
    mfa_secret = Column(String(32), nullable=True)  # TOTP support
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Profile information
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=True)
    
    # Status tracking
    status = Column(SAEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    hire_date = Column(Date, nullable=True)
    
    # Position information
    position = Column(String(100), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        {'extend_existing': True}
        # Inherited from EnhancedBase: created_at, updated_at indexes
    )