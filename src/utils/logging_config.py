"""
Logging Configuration for WIZARD-2.1

Centralized logging configuration and setup.
"""

import logging
import logging.handlers
from pathlib import Path
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO", log_dir: Optional[str] = None) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./logs)
    """
    try:
        # Set log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        else:
            log_dir = Path(log_dir)
            
        # Create log directory if it doesn't exist
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # Application log file handler
        app_log_file = log_dir / "wizard_app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Debug log file handler
        debug_log_file = log_dir / "wizard_debug.log"
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(debug_handler)
        
        # Error log file handler
        error_log_file = log_dir / "wizard_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Server communication log file handler
        server_log_file = log_dir / "wizard_server.log"
        server_handler = logging.handlers.RotatingFileHandler(
            server_log_file, maxBytes=10*1024*1024, backupCount=5
        )
        server_handler.setLevel(logging.INFO)
        server_handler.setFormatter(detailed_formatter)
        
        # Create server logger
        server_logger = logging.getLogger("server")
        server_logger.addHandler(server_handler)
        server_logger.setLevel(logging.INFO)
        server_logger.propagate = False
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized successfully")
        logger.info(f"Log directory: {log_dir}")
        logger.info(f"Log level: {log_level}")
        
    except Exception as e:
        print(f"Error setting up logging: {e}", file=sys.stderr)
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func):
    """
    Decorator to log function calls.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    return wrapper


def log_performance(func):
    """
    Decorator to log function performance.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f} seconds with error: {e}")
            raise
    return wrapper
