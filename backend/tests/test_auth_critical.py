"""
Critical authentication flow tests - 100% coverage required.
Tests all authentication scenarios, security edge cases, and token handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.api.routes.auth import (
    create_access_token,
    create_refresh_token,
    get_client_ip,
    login,
    refresh_token,
    logout,
    get_current_user,
    get_current_admin,
    get_current_manager
)
from app.models.user import User, UserRole
from app.core.config import get_settings


@pytest.fixture
def mock_settings():
    """Mock application settings"""
    settings = Mock()
    settings.SECRET_KEY = "test-secret-key"
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.REFRESH_TOKEN_EXPIRE_MINUTES = 1440
    return settings


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.role = Mock()
    user.role.name = "user"
    return user


@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "admin"
    user.email = "admin@example.com"
    user.role = UserRole.admin
    return user


@pytest.fixture
def mock_request():
    """Mock FastAPI request"""
    request = Mock(spec=Request)
    request.headers = {}
    request.client = Mock()
    request.client.host = "127.0.0.1"
    return request


class TestTokenCreation:
    """Test JWT token creation functions - CRITICAL"""
    
    @patch('app.api.routes.auth.get_settings')
    def test_create_access_token_success(self, mock_get_settings, mock_settings):
        """CRITICAL: Test access token creation"""
        mock_get_settings.return_value = mock_settings
        
        data = {"sub": "testuser", "role": "user"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        # Verify token can be decoded
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=[mock_settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "user"
        assert "exp" in decoded
        
    @patch('app.api.routes.auth.get_settings')
    def test_create_refresh_token_success(self, mock_get_settings, mock_settings):
        """CRITICAL: Test refresh token creation"""
        mock_get_settings.return_value = mock_settings
        
        data = {"sub": "testuser", "role": "user"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        # Verify token can be decoded and has correct type
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=[mock_settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "user"
        assert decoded["type"] == "refresh"
        assert "exp" in decoded
        
    def test_token_expiration_times(self):
        """CRITICAL: Verify token expiration times are set correctly"""
        with patch('app.api.routes.auth.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.SECRET_KEY = "test-key"
            mock_settings.ALGORITHM = "HS256"
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
            mock_settings.REFRESH_TOKEN_EXPIRE_MINUTES = 1440
            mock_get_settings.return_value = mock_settings
            
            # Create tokens
            access_token = create_access_token({"sub": "test"})
            refresh_token = create_refresh_token({"sub": "test"})
            
            # Decode and check expiration
            access_decoded = jwt.decode(access_token, "test-key", algorithms=["HS256"])
            refresh_decoded = jwt.decode(refresh_token, "test-key", algorithms=["HS256"])
            
            # Access token should expire in 30 minutes
            access_exp = datetime.fromtimestamp(access_decoded["exp"], tz=timezone.utc)
            expected_access_exp = datetime.now(timezone.utc) + timedelta(minutes=30)
            assert abs((access_exp - expected_access_exp).total_seconds()) < 60
            
            # Refresh token should expire in 24 hours
            refresh_exp = datetime.fromtimestamp(refresh_decoded["exp"], tz=timezone.utc)
            expected_refresh_exp = datetime.now(timezone.utc) + timedelta(minutes=1440)
            assert abs((refresh_exp - expected_refresh_exp).total_seconds()) < 60


class TestIPAddressExtraction:
    """Test IP address extraction - CRITICAL for audit logging"""
    
    def test_get_client_ip_x_forwarded_for(self, mock_request):
        """CRITICAL: Test IP extraction from X-Forwarded-For header"""
        mock_request.headers = {"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}
        
        ip = get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
        
    def test_get_client_ip_x_real_ip(self, mock_request):
        """CRITICAL: Test IP extraction from X-Real-IP header"""
        mock_request.headers = {"X-Real-IP": "203.0.113.1"}
        
        ip = get_client_ip(mock_request)
        
        assert ip == "203.0.113.1"
        
    def test_get_client_ip_client_host(self, mock_request):
        """CRITICAL: Test IP extraction from client host"""
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"
        
        ip = get_client_ip(mock_request)
        
        assert ip == "192.168.1.1"
        
    def test_get_client_ip_no_client(self, mock_request):
        """CRITICAL: Test IP extraction when no client info available"""
        mock_request.headers = {}
        mock_request.client = None
        
        ip = get_client_ip(mock_request)
        
        assert ip == "unknown"


class TestLoginEndpoint:
    """Test login endpoint - CRITICAL authentication flow"""
    
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.UserService')
    @patch('app.api.routes.auth.log_action')
    @patch('app.api.routes.auth.get_client_ip')
    async def test_login_success(self, mock_get_ip, mock_log_action, mock_user_service, mock_request, mock_user):
        """CRITICAL: Test successful login flow"""
        # Setup mocks
        mock_get_ip.return_value = "192.168.1.1"
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        mock_service_instance.authenticate_user.return_value = mock_user
        mock_db = Mock()
        
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "testpass"
        
        # Execute login
        response = await login(mock_request, form_data, mock_db)
        
        # Verify response structure
        assert "access_token" in response.body.decode()
        assert "token_type" in response.body.decode()
        
        # Verify logging was called
        mock_log_action.assert_called_once_with("testuser", "LOGIN", "ip=192.168.1.1")
        
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.UserService')
    async def test_login_invalid_credentials(self, mock_user_service, mock_request):
        """CRITICAL: Test login with invalid credentials"""
        # Setup mocks
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        mock_service_instance.authenticate_user.return_value = None
        mock_db = Mock()
        
        form_data = Mock(spec=OAuth2PasswordRequestForm)
        form_data.username = "testuser"
        form_data.password = "wrongpass"
        
        # Execute login and expect failure
        with pytest.raises(HTTPException) as exc_info:
            await login(mock_request, form_data, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Неверное имя пользователя или пароль" in str(exc_info.value.detail)


class TestRefreshTokenEndpoint:
    """Test refresh token endpoint - CRITICAL for token renewal"""
    
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.UserService')
    @patch('app.api.routes.auth.log_action')
    @patch('app.api.routes.auth.get_client_ip')
    @patch('app.api.routes.auth.get_settings')
    async def test_refresh_token_success(self, mock_get_settings, mock_get_ip, mock_log_action, mock_user_service, mock_request, mock_user, mock_settings):
        """CRITICAL: Test successful token refresh"""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_ip.return_value = "192.168.1.1"
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        mock_service_instance.get_user_by_username.return_value = mock_user
        mock_db = Mock()
        mock_response = Mock(spec=Response)
        
        # Create valid refresh token
        refresh_token_data = {
            "sub": "testuser",
            "role": "user",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        valid_refresh_token = jwt.encode(refresh_token_data, mock_settings.SECRET_KEY, algorithm=mock_settings.ALGORITHM)
        
        # Execute refresh
        result = await refresh_token(mock_request, mock_response, valid_refresh_token, mock_db)
        
        # Verify response
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        
        # Verify logging
        mock_log_action.assert_called_once_with("testuser", "REFRESH_TOKEN", "ip=192.168.1.1")
        
    @pytest.mark.asyncio
    async def test_refresh_token_missing(self, mock_request):
        """CRITICAL: Test refresh when token is missing"""
        mock_response = Mock(spec=Response)
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, mock_response, None, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Refresh token отсутствует" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.get_settings')
    async def test_refresh_token_invalid_type(self, mock_get_settings, mock_request, mock_settings):
        """CRITICAL: Test refresh with access token instead of refresh token"""
        mock_get_settings.return_value = mock_settings
        mock_response = Mock(spec=Response)
        mock_db = Mock()
        
        # Create access token (not refresh token)
        access_token_data = {
            "sub": "testuser",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        invalid_token = jwt.encode(access_token_data, mock_settings.SECRET_KEY, algorithm=mock_settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_request, mock_response, invalid_token, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Недействительный refresh token" in str(exc_info.value.detail)


class TestCurrentUserAuthentication:
    """Test current user authentication - CRITICAL for protected routes"""
    
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.UserService')
    @patch('app.api.routes.auth.get_settings')
    async def test_get_current_user_success(self, mock_get_settings, mock_user_service, mock_user, mock_settings):
        """CRITICAL: Test successful current user retrieval"""
        mock_get_settings.return_value = mock_settings
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        mock_service_instance.get_user_by_username.return_value = mock_user
        mock_db = Mock()
        
        # Create valid token
        token_data = {
            "sub": "testuser",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        valid_token = jwt.encode(token_data, mock_settings.SECRET_KEY, algorithm=mock_settings.ALGORITHM)
        
        user = await get_current_user(valid_token, mock_db)
        
        assert user == mock_user
        mock_service_instance.get_user_by_username.assert_called_once_with("testuser")
        
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.get_settings')
    async def test_get_current_user_invalid_token(self, mock_get_settings, mock_settings):
        """CRITICAL: Test current user with invalid token"""
        mock_get_settings.return_value = mock_settings
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Неверные учетные данные" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.UserService')
    @patch('app.api.routes.auth.get_settings')
    async def test_get_current_user_role_mismatch(self, mock_get_settings, mock_user_service, mock_user, mock_settings):
        """CRITICAL: Test current user when role in token doesn't match database"""
        mock_get_settings.return_value = mock_settings
        mock_service_instance = Mock()
        mock_user_service.return_value = mock_service_instance
        mock_user.role.name = "user"  # User is regular user in DB
        mock_service_instance.get_user_by_username.return_value = mock_user
        mock_db = Mock()
        
        # Create token claiming admin role
        token_data = {
            "sub": "testuser",
            "role": "admin",  # Token claims admin but user is regular user
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        valid_token = jwt.encode(token_data, mock_settings.SECRET_KEY, algorithm=mock_settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(valid_token, mock_db)
        
        assert exc_info.value.status_code == 401


class TestRoleBasedAccess:
    """Test role-based access control - CRITICAL for authorization"""
    
    @pytest.mark.asyncio
    async def test_get_current_admin_success(self, mock_admin_user):
        """CRITICAL: Test admin access control success"""
        result = await get_current_admin(mock_admin_user)
        assert result == mock_admin_user
        
    @pytest.mark.asyncio
    async def test_get_current_admin_insufficient_role(self, mock_user):
        """CRITICAL: Test admin access control failure"""
        mock_user.role = UserRole.user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Недостаточно прав" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio
    async def test_get_current_manager_admin_access(self, mock_admin_user):
        """CRITICAL: Test manager endpoint allows admin access"""
        result = await get_current_manager(mock_admin_user)
        assert result == mock_admin_user
        
    @pytest.mark.asyncio
    async def test_get_current_manager_manager_access(self):
        """CRITICAL: Test manager endpoint allows manager access"""
        manager_user = Mock()
        manager_user.role = UserRole.manager
        
        result = await get_current_manager(manager_user)
        assert result == manager_user
        
    @pytest.mark.asyncio
    async def test_get_current_manager_user_denied(self, mock_user):
        """CRITICAL: Test manager endpoint denies regular user"""
        mock_user.role = UserRole.user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_manager(mock_user)
        
        assert exc_info.value.status_code == 403


class TestLogoutEndpoint:
    """Test logout endpoint - CRITICAL for session termination"""
    
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.log_action')
    @patch('app.api.routes.auth.get_client_ip')
    async def test_logout_success(self, mock_get_ip, mock_log_action, mock_request):
        """CRITICAL: Test successful logout"""
        mock_get_ip.return_value = "192.168.1.1"
        mock_response = Mock(spec=Response)
        
        result = await logout(mock_request, mock_response)
        
        assert result["detail"] == "Выход выполнен"
        mock_log_action.assert_called_once_with("unknown", "LOGOUT", "ip=192.168.1.1")


class TestSecurityEdgeCases:
    """Test security edge cases and attack vectors - CRITICAL"""
    
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.get_settings')
    async def test_expired_token_handling(self, mock_get_settings, mock_settings):
        """CRITICAL: Test handling of expired tokens"""
        mock_get_settings.return_value = mock_settings
        mock_db = Mock()
        
        # Create expired token
        expired_token_data = {
            "sub": "testuser",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_token_data, mock_settings.SECRET_KEY, algorithm=mock_settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(expired_token, mock_db)
        
        assert exc_info.value.status_code == 401
        
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.get_settings')
    async def test_malformed_token_handling(self, mock_get_settings, mock_settings):
        """CRITICAL: Test handling of malformed tokens"""
        mock_get_settings.return_value = mock_settings
        mock_db = Mock()
        
        malformed_tokens = [
            "not.a.token",
            "malformed_token_string",
            "",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.malformed",
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_db)
            assert exc_info.value.status_code == 401
            
    @pytest.mark.asyncio
    @patch('app.api.routes.auth.get_settings')
    async def test_token_with_wrong_signature(self, mock_get_settings, mock_settings):
        """CRITICAL: Test handling of tokens with wrong signature"""
        mock_get_settings.return_value = mock_settings
        mock_db = Mock()
        
        # Create token with wrong secret
        token_data = {
            "sub": "testuser",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        wrong_signature_token = jwt.encode(token_data, "wrong_secret", algorithm=mock_settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(wrong_signature_token, mock_db)
        
        assert exc_info.value.status_code == 401


class TestConcurrentAuthentication:
    """Test concurrent authentication scenarios - CRITICAL for production"""
    
    @pytest.mark.asyncio
    async def test_multiple_token_refresh_attempts(self):
        """CRITICAL: Test multiple concurrent refresh token attempts"""
        # This would test race conditions in token refresh
        # Implementation would depend on actual concurrency requirements
        pass
        
    @pytest.mark.asyncio
    async def test_session_invalidation_security(self):
        """CRITICAL: Test that invalidated sessions cannot be reused"""
        # This would test session invalidation mechanisms
        pass