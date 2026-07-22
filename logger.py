import os
import sys
import logging
from datetime import datetime

# Папка, где лежат все данные Cortex
LOG_DIR = os.path.expanduser("~/.cortex")
LOG_FILE = os.path.join(LOG_DIR, "cortex.log")

class ColorFormatter(logging.Formatter):
    """Кастомный форматер, чтобы в терминале логи были цветными"""
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: f"{GREY}%(asctime)s - [%(levelname)s] - %(message)s{RESET}",
        logging.INFO: f"{GREY}%(asctime)s - [%(levelname)s] - %(message)s{RESET}",
        logging.WARNING: f"{YELLOW}%(asctime)s - [%(levelname)s] - %(message)s{RESET}",
        logging.ERROR: f"{RED}%(asctime)s - [%(levelname)s] - %(message)s{RESET}",
        logging.CRITICAL: f"{BOLD_RED}%(asctime)s - [%(levelname)s] - %(message)s{RESET}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def get_logger(name: str = "Cortex") -> logging.Logger:
    """
    Создает и возвращает настроенный логгер.
    Использование: from logger import get_logger \n logger = get_logger()
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(ColorFormatter())
    # logger.addHandler(console_handler)

    return logger


logger = get_logger("Cortex")