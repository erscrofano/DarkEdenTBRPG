"""Logging system for the game"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from ..save.system import get_save_dir


class GameLogger:
    """Centralized logging system for the game"""
    
    _logger = None
    _initialized = False
    
    @classmethod
    def get_logger(cls):
        """Get or create the game logger"""
        if not cls._initialized:
            cls._setup_logger()
        return cls._logger
    
    @classmethod
    def _setup_logger(cls):
        """Set up the logger with file and console handlers"""
        logger = logging.getLogger('rpg_game')
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            cls._logger = logger
            cls._initialized = True
            return
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler - logs everything
        try:
            log_dir = get_save_dir() / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'game.log'
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # If we can't create log file, just log to console
            sys.stderr.write(f"Warning: Could not create log file: {e}\n")
        
        # Console handler - only warnings and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        cls._logger = logger
        cls._initialized = True
    
    @classmethod
    def debug(cls, message: str):
        """Log debug message"""
        cls.get_logger().debug(message)
    
    @classmethod
    def info(cls, message: str):
        """Log info message"""
        cls.get_logger().info(message)
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message"""
        cls.get_logger().warning(message)
    
    @classmethod
    def error(cls, message: str, exc_info=False):
        """Log error message"""
        cls.get_logger().error(message, exc_info=exc_info)
    
    @classmethod
    def exception(cls, message: str):
        """Log exception with traceback"""
        cls.get_logger().exception(message)


# Convenience functions
def log_debug(message: str):
    """Log debug message"""
    GameLogger.debug(message)


def log_info(message: str):
    """Log info message"""
    GameLogger.info(message)


def log_warning(message: str):
    """Log warning message"""
    GameLogger.warning(message)


def log_error(message: str, exc_info=False):
    """Log error message"""
    GameLogger.error(message, exc_info=exc_info)


def log_exception(message: str):
    """Log exception with traceback"""
    GameLogger.exception(message)

