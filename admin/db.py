"""
Database connection management for the XumotjBot Admin Panel.
"""
import logging
from typing import Callable, List
from mongoengine import connect, disconnect

from config import DB_NAME, MONGO_URI

# Configure logging
logger = logging.getLogger("xumotjbot.admin.db")

def setup_database() -> None:
    """Connect to MongoDB database."""
    try:
        connect(host=MONGO_URI)
        logger.info(f"Connected to database: {DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def close_database() -> None:
    """Disconnect from MongoDB database."""
    disconnect()
    logger.info("Disconnected from database")


def get_startup_handlers() -> List[Callable]:
    """Return list of startup handlers."""
    return [setup_database]


def get_shutdown_handlers() -> List[Callable]:
    """Return list of shutdown handlers."""
    return [close_database]
