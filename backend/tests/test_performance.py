import pytest
import time
from fastapi.testclient import TestClient

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.slow
def test_booking_list_performance(auth_client, db_session):
    """Тест производительности получения списка бронирований."""
    # Создаем несколько тестовых бронирований для нагрузки
    from datetime import datetime, timezone, timedelta
    
    for i in range(10):
        future_date = datetime.now(timezone.utc) + timedelta(days=i+1)
        start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
        
        booking_data = {
            "date": future_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 1000.0 + i,
            "client_name": f"Client {i}",
            "client_phone": f"+7900123456{i:02d}"
        }
        
        auth_client.post("/api/bookings/", json=booking_data)
    
    # Тестируем производительность получения списка
    start_time = time.time()
    response = auth_client.get("/api/bookings/")
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Проверяем, что запрос выполнился быстро (менее 1 секунды)
    assert execution_time < 1.0
    assert response.status_code == 200
    
    print(f"Booking list retrieval took {execution_time:.3f} seconds")

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.slow
def test_booking_search_performance(auth_client, db_session):
    """Тест производительности поиска бронирований."""
    # Создаем много бронирований для тестирования поиска
    from datetime import datetime, timezone, timedelta
    
    for i in range(50):
        future_date = datetime.now(timezone.utc) + timedelta(days=i+1)
        start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
        
        booking_data = {
            "date": future_date.isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_price": 1000.0 + i,
            "client_name": f"Client {i}",
            "client_phone": f"+7900123456{i:02d}"
        }
        
        auth_client.post("/api/bookings/", json=booking_data)
    
    # Тестируем производительность поиска по клиенту
    start_time = time.time()
    response = auth_client.get("/api/bookings/?client_name=Client 25")
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Проверяем, что поиск выполнился быстро (менее 0.5 секунды)
    assert execution_time < 0.5
    assert response.status_code == 200
    
    print(f"Booking search took {execution_time:.3f} seconds")

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_requests_performance(auth_client, db_session):
    """Тест производительности при одновременных запросах."""
    import threading
    import concurrent.futures
    
    def make_request():
        return auth_client.get("/api/bookings/")
    
    # Выполняем 10 одновременных запросов
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Проверяем, что все запросы выполнились успешно
    for response in responses:
        assert response.status_code == 200
    
    # Проверяем, что общее время выполнения разумное (менее 2 секунд)
    assert execution_time < 2.0
    
    print(f"10 concurrent requests took {execution_time:.3f} seconds")

@pytest.mark.performance
@pytest.mark.integration
def test_database_connection_pool_performance(auth_client, db_session):
    """Тест производительности пула соединений с базой данных."""
    # Выполняем множество запросов подряд для тестирования пула соединений
    start_time = time.time()
    
    for i in range(20):
        response = auth_client.get("/api/bookings/")
        assert response.status_code == 200
    
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Проверяем, что все запросы выполнились быстро
    assert execution_time < 5.0
    
    print(f"20 sequential requests took {execution_time:.3f} seconds")

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.slow
def test_memory_usage_performance(auth_client, db_session):
    """Тест использования памяти при работе с большими объемами данных."""
    import psutil
    import os
    
    # Получаем текущее использование памяти
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Выполняем множество запросов
    for i in range(30):
        response = auth_client.get("/api/bookings/")
        assert response.status_code == 200
    
    # Получаем использование памяти после запросов
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    memory_increase = final_memory - initial_memory
    
    # Проверяем, что увеличение использования памяти разумное (менее 100 MB)
    assert memory_increase < 100.0
    
    print(f"Memory usage: {initial_memory:.1f} MB -> {final_memory:.1f} MB (increase: {memory_increase:.1f} MB)")

@pytest.mark.performance
@pytest.mark.unit
def test_response_size_performance(auth_client, db_session):
    """Тест размера ответов API."""
    # Получаем список бронирований
    response = auth_client.get("/api/bookings/")
    assert response.status_code == 200
    
    # Проверяем размер ответа
    response_size = len(response.content)
    
    # Размер ответа должен быть разумным (менее 1 MB)
    assert response_size < 1024 * 1024
    
    print(f"Response size: {response_size} bytes")

@pytest.mark.performance
@pytest.mark.unit
def test_api_response_time_consistency(auth_client, db_session):
    """Тест консистентности времени ответа API."""
    response_times = []
    
    # Выполняем несколько запросов и измеряем время
    for i in range(10):
        start_time = time.time()
        response = auth_client.get("/api/bookings/")
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append(end_time - start_time)
    
    # Вычисляем статистику
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    # Проверяем, что разброс времени ответа разумный
    assert max_time - min_time < 0.5  # Разброс менее 0.5 секунды
    assert avg_time < 0.3  # Среднее время менее 0.3 секунды
    
    print(f"Response times: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
