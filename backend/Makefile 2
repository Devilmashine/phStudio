.PHONY: help test test-unit test-integration test-security test-performance test-all test-coverage test-fast test-slow clean install-deps

# Переменные
PYTHON = python
PIP = pip
PYTEST = pytest
VENV = venv
ACTIVATE = source $(VENV)/bin/activate

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install-deps: ## Установить зависимости для тестирования
	@echo "$(GREEN)Устанавливаю зависимости для тестирования...$(NC)"
	$(ACTIVATE) && $(PIP) install -r requirements-dev.txt
	$(ACTIVATE) && $(PIP) install pytest-cov pytest-mock pytest-asyncio

test: ## Запустить все тесты
	@echo "$(GREEN)Запускаю все тесты...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -v

test-unit: ## Запустить только unit-тесты (быстрые)
	@echo "$(GREEN)Запускаю unit-тесты...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "unit" -v

test-integration: ## Запустить только интеграционные тесты
	@echo "$(GREEN)Запускаю интеграционные тесты...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "integration" -v

test-security: ## Запустить тесты безопасности
	@echo "$(GREEN)Запускаю тесты безопасности...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "security" -v

test-performance: ## Запустить тесты производительности
	@echo "$(GREEN)Запускаю тесты производительности...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "performance" -v

test-fast: ## Запустить быстрые тесты (без slow маркера)
	@echo "$(GREEN)Запускаю быстрые тесты...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "not slow" -v

test-slow: ## Запустить медленные тесты
	@echo "$(GREEN)Запускаю медленные тесты...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "slow" -v

test-models: ## Запустить тесты моделей
	@echo "$(GREEN)Запускаю тесты моделей...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "models" -v

test-api: ## Запустить тесты API
	@echo "$(GREEN)Запускаю тесты API...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "api" -v

test-schemas: ## Запустить тесты схем
	@echo "$(GREEN)Запускаю тесты схем...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "schemas" -v

test-services: ## Запустить тесты сервисов
	@echo "$(GREEN)Запускаю тесты сервисов...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "services" -v

test-edge-cases: ## Запустить тесты edge cases
	@echo "$(GREEN)Запускаю тесты edge cases...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "edge_cases" -v

test-coverage: ## Запустить тесты с покрытием кода
	@echo "$(GREEN)Запускаю тесты с покрытием кода...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-all: ## Запустить все тесты с подробным отчетом
	@echo "$(GREEN)Запускаю все тесты с подробным отчетом...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -v --tb=long --durations=10

test-debug: ## Запустить тесты в режиме отладки
	@echo "$(GREEN)Запускаю тесты в режиме отладки...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -v -s --tb=long

test-specific: ## Запустить конкретный тест (использовать: make test-specific TEST=test_name)
	@echo "$(GREEN)Запускаю тест: $(TEST)$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -k "$(TEST)" -v

test-file: ## Запустить тесты из конкретного файла (использовать: make test-file FILE=test_file.py)
	@echo "$(GREEN)Запускаю тесты из файла: $(FILE)$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/$(FILE) -v

clean: ## Очистить временные файлы и отчеты
	@echo "$(GREEN)Очищаю временные файлы...$(NC)"
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Запустить линтеры
	@echo "$(GREEN)Запускаю линтеры...$(NC)"
	$(ACTIVATE) && flake8 app/ tests/
	$(ACTIVATE) && black --check app/ tests/
	$(ACTIVATE) && isort --check-only app/ tests/

format: ## Форматировать код
	@echo "$(GREEN)Форматирую код...$(NC)"
	$(ACTIVATE) && black app/ tests/
	$(ACTIVATE) && isort app/ tests/

install-test-deps: ## Установить зависимости для тестирования
	@echo "$(GREEN)Устанавливаю зависимости для тестирования...$(NC)"
	$(ACTIVATE) && $(PIP) install pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist

install-dev-deps: ## Установить все dev-зависимости
	@echo "$(GREEN)Устанавливаю все dev-зависимости...$(NC)"
	$(ACTIVATE) && $(PIP) install -r requirements-dev.txt

setup-test-env: ## Настроить тестовое окружение
	@echo "$(GREEN)Настраиваю тестовое окружение...$(NC)"
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	$(ACTIVATE) && $(PIP) install -r requirements-dev.txt
	$(ACTIVATE) && $(PIP) install pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist

# Команды для CI/CD
ci-test: ## Запустить тесты для CI/CD
	@echo "$(GREEN)Запускаю тесты для CI/CD...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=80 --junitxml=test-results.xml

ci-test-fast: ## Запустить быстрые тесты для CI/CD
	@echo "$(GREEN)Запускаю быстрые тесты для CI/CD...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "not slow" --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=80 --junitxml=test-results.xml

# Команды для профилирования
profile: ## Запустить тесты с профилированием
	@echo "$(GREEN)Запускаю тесты с профилированием...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --profile --profile-svg

# Команды для параллельного выполнения
test-parallel: ## Запустить тесты параллельно
	@echo "$(GREEN)Запускаю тесты параллельно...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -n auto --dist=loadfile

# Команды для конкретных окружений
test-db: ## Запустить тесты с базой данных
	@echo "$(GREEN)Запускаю тесты с базой данных...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "integration" -v

test-no-db: ## Запустить тесты без базы данных
	@echo "$(GREEN)Запускаю тесты без базы данных...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -m "unit" -v

# Команды для отчетов
report-html: ## Создать HTML отчет о покрытии
	@echo "$(GREEN)Создаю HTML отчет о покрытии...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=html
	@echo "$(GREEN)Отчет создан в папке htmlcov/$(NC)"

report-xml: ## Создать XML отчет о покрытии
	@echo "$(GREEN)Создаю XML отчет о покрытии...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=xml
	@echo "$(GREEN)Отчет создан в файле coverage.xml$(NC)"

# Команды для мониторинга
monitor: ## Мониторинг тестов в реальном времени
	@echo "$(GREEN)Запускаю мониторинг тестов...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ --tb=short -v --durations=0

# Команды для отладки
debug-test: ## Запустить тесты в режиме отладки с остановкой на ошибках
	@echo "$(GREEN)Запускаю тесты в режиме отладки...$(NC)"
	$(ACTIVATE) && $(PYTEST) tests/ -v -s --pdb --tb=long

# Команды для проверки качества
quality-check: ## Проверить качество кода
	@echo "$(GREEN)Проверяю качество кода...$(NC)"
	$(ACTIVATE) && flake8 app/ tests/
	$(ACTIVATE) && black --check app/ tests/
	$(ACTIVATE) && isort --check-only app/ tests/
	$(ACTIVATE) && $(PYTEST) tests/ --cov=app --cov-report=term-missing --cov-fail-under=80

# Команды для подготовки к деплою
pre-deploy: ## Подготовка к деплою (запуск всех проверок)
	@echo "$(GREEN)Подготавливаю к деплою...$(NC)"
	$(MAKE) clean
	$(MAKE) quality-check
	$(MAKE) test-all
	@echo "$(GREEN)Все проверки пройдены успешно!$(NC)"
