from backend.app.utils.auth import require_role, UserRole
from backend.app.models.user import UserSchema
import pytest

def test_require_role_admin():
    user = UserSchema(username="admin", role=UserRole.admin)
    assert require_role(UserRole.admin)(user) == user

def test_require_role_forbidden():
    user = UserSchema(username="user", role=UserRole.user)
    with pytest.raises(Exception):
        require_role(UserRole.admin)(user) 