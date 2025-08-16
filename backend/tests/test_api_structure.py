import pytest

@pytest.mark.unit
@pytest.mark.api
def test_api_routes_import():
    """Тест импорта API роутов."""
    # Проверяем, что все роуты могут быть импортированы
    from ..app.api.routes import auth, booking, calendar_events, clients, gallery, news, settings
    
    assert auth is not None
    assert booking is not None
    assert calendar_events is not None
    assert clients is not None
    assert gallery is not None
    assert news is not None
    assert settings is not None

@pytest.mark.unit
@pytest.mark.api
def test_api_router_structure():
    """Тест структуры роутеров."""
    from ..app.api.routes.auth import router as auth_router
    from ..app.api.routes.booking import router as booking_router
    from ..app.api.routes.calendar_events import router as calendar_router
    from ..app.api.routes.clients import router as clients_router
    from ..app.api.routes.gallery import router as gallery_router
    from ..app.api.routes.news import router as news_router
    from ..app.api.routes.settings import router as settings_router
    
    # Проверяем, что роутеры существуют и имеют атрибут routes
    assert hasattr(auth_router, 'routes')
    assert hasattr(booking_router, 'routes')
    assert hasattr(calendar_router, 'routes')
    assert hasattr(clients_router, 'routes')
    assert hasattr(gallery_router, 'routes')
    assert hasattr(news_router, 'routes')
    assert hasattr(settings_router, 'routes')

@pytest.mark.unit
@pytest.mark.api
def test_main_app_structure():
    """Тест структуры главного приложения."""
    from ..app.main import app
    
    # Проверяем, что приложение существует
    assert app is not None
    assert hasattr(app, 'routes')

@pytest.mark.unit
@pytest.mark.api
def test_dependencies_import():
    """Тест импорта зависимостей."""
    from ..app.core.config import get_settings
    from ..app.core.database import get_db
    from ..app.core.rate_limiter import default_rate_limit
    
    # Проверяем, что зависимости существуют
    assert callable(get_settings)
    assert callable(get_db)
    assert callable(default_rate_limit)
