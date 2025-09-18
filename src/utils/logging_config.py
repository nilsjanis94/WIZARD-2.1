"""
Logging Configuration for WIZARD-2.1

Centralized logging configuration and setup.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
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
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        # Console handler - disabled for production, logs go to files only
        # console_handler = logging.StreamHandler(sys.stdout)
        # console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(simple_formatter)
        # root_logger.addHandler(console_handler)

        # Application log file handler
        app_log_file = log_dir / "wizard_app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)

        # Debug log file handler
        debug_log_file = log_dir / "wizard_debug.log"
        debug_handler = logging.handlers.RotatingFileHandler(
            debug_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(debug_handler)

        # Error log file handler
        error_log_file = log_dir / "wizard_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)

        # Server communication log file handler
        server_log_file = log_dir / "wizard_server.log"
        server_handler = logging.handlers.RotatingFileHandler(
            server_log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        server_handler.setLevel(logging.INFO)
        server_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(server_handler)

        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized successfully")
        logger.info("Log directory: %s", log_dir)
        logger.info("Log level: %s", log_level)

    except (OSError, PermissionError) as e:
        print(f"File system error setting up logging: {e}", file=sys.stderr)
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    except Exception as e:
        print(f"Unexpected error setting up logging: {e}", file=sys.stderr)
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
        logger.debug("Calling %s with args=%s, kwargs=%s", func.__name__, args, kwargs)
        try:
            result = func(*args, **kwargs)
            logger.debug("%s completed successfully", func.__name__)
            return result
        except (TypeError, AttributeError) as e:
            logger.error("Function signature error in %s: %s", func.__name__, e)
            raise
        except Exception as e:
            logger.error("%s failed with error: %s", func.__name__, e)
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
            logger.info("%s completed in %.3f seconds", func.__name__, duration)
            return result
        except (TypeError, AttributeError) as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(
                "Function signature error in %s after %.3f seconds: %s",
                func.__name__,
                duration,
                e,
            )
            raise
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(
                "%s failed after %.3f seconds with error: %s",
                func.__name__,
                duration,
                e,
            )
            raise

    return wrapper
