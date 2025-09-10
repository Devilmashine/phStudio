"""
Authentication and authorization utilities
"""

from enum import Enum
from typing import Callable, Any
from fastapi import HTTPException, status
from functools import wraps


class UserRole(str, Enum):
    """User roles for authorization"""
    admin = "admin"
    manager = "manager"
    employee = "employee"
    user = "user"


def require_role(required_role: UserRole) -> Callable:
    """
    Decorator to require specific user role for access.
    
    Args:
        required_role: Minimum required role level
        
    Returns:
        Decorated function that checks user role
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if not user or not hasattr(user, 'role'):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authentication required"
                )
            
            # Define role hierarchy
            role_hierarchy = {
                UserRole.user: 1,
                UserRole.employee: 2,
                UserRole.manager: 3,
                UserRole.admin: 4,
            }
            
            user_level = role_hierarchy.get(user.role, 0)
            required_level = role_hierarchy.get(required_role, 999)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role}"
                )
            
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


def check_permission(user: Any, resource: str, action: str) -> bool:
    """
    Check if user has permission for specific resource and action.
    
    Args:
        user: User object with role
        resource: Resource name (e.g., 'bookings', 'employees')
        action: Action type (e.g., 'read', 'write', 'delete')
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user or not hasattr(user, 'role'):
        return False
    
    # Admin has all permissions
    if user.role == UserRole.admin:
        return True
    
    # Manager permissions
    if user.role == UserRole.manager:
        if resource in ['bookings', 'calendar', 'kanban', 'statistics']:
            return True
        if resource == 'employees' and action in ['read']:
            return True
    
    # Employee permissions
    if user.role == UserRole.employee:
        if resource in ['bookings', 'calendar'] and action in ['read', 'write']:
            return True
        if resource == 'kanban' and action in ['read']:
            return True
    
    # User permissions (clients)
    if user.role == UserRole.user:
        if resource == 'bookings' and action in ['read', 'write']:
            # Only their own bookings
            return True
    
    return False


def require_permission(resource: str, action: str) -> Callable:
    """
    Decorator to require specific permission for resource access.
    
    Args:
        resource: Resource name
        action: Action type
        
    Returns:
        Decorated function that checks user permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if not check_permission(user, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Permission required: {action} {resource}"
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator
