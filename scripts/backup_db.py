import os
import sys
import logging
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def backup_database():
    load_dotenv()
    
    # Получаем параметры подключения из DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not set")

    try:
        # Создаем директорию для бэкапов если её нет
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)

        # Формируем имя файла с текущей датой
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')

        # Выполняем pg_dump
        os.system(f'pg_dump {database_url} > {backup_file}')
        
        # Проверяем размер файла
        if os.path.getsize(backup_file) > 0:
            logger.info(f"Backup created successfully: {backup_file}")
        else:
            raise Exception("Backup file is empty")

        # Удаляем старые бэкапы (оставляем только последние 5)
        backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)])
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                logger.info(f"Removed old backup: {old_backup}")

    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise

if __name__ == '__main__':
    backup_database()
