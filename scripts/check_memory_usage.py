import os
import psutil
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_memory_usage():
    """
    Проверяет использование памяти и логирует предупреждение,
    если использование превышает 80%
    """
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    logger.info(f"Current memory usage: {memory_usage}%")
    
    if memory_usage > 80:
        logger.warning(f"High memory usage detected: {memory_usage}%")
        return False
    return True

def check_disk_usage():
    """
    Проверяет использование диска и логирует предупреждение,
    если свободного места меньше 20%
    """
    disk = psutil.disk_usage('/')
    disk_usage = 100 - disk.percent
    
    logger.info(f"Free disk space: {disk_usage}%")
    
    if disk_usage < 20:
        logger.warning(f"Low disk space detected: {disk_usage}% free")
        return False
    return True

def check_cpu_usage():
    """
    Проверяет загрузку CPU и логирует предупреждение,
    если загрузка превышает 90%
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    
    logger.info(f"CPU usage: {cpu_usage}%")
    
    if cpu_usage > 90:
        logger.warning(f"High CPU usage detected: {cpu_usage}%")
        return False
    return True

def main():
    status = True
    
    if not check_memory_usage():
        status = False
    
    if not check_disk_usage():
        status = False
    
    if not check_cpu_usage():
        status = False
    
    if not status:
        logger.error("Resource usage checks failed")
        exit(1)
    
    logger.info("All resource usage checks passed")

if __name__ == "__main__":
    main()
