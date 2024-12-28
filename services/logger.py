from loguru import logger
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Add handler for events
logger.add(
    "logs/events.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    filter=lambda record: record["level"].name == "INFO",
    encoding="utf-8",
    rotation="10 MB",
    compression="zip"
)

# Add handler for errors
logger.add(
    "logs/errors.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}\n{exception}",
    filter=lambda record: record["level"].name == "ERROR",
    encoding="utf-8",
    rotation="10 MB",
    compression="zip"
)

def log_event(user_id: int, event: str):
    """Log user events in format: user_id | event"""
    logger.info(f"{user_id} | {event}")

def log_error(user_id: int, error: Exception, context: str = ""):
    """Log errors with user_id and context"""
    logger.error(f"{user_id} | {context} | {str(error)}")
