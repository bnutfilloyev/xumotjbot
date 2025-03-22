"""
Configuration settings for the XumotjBot Admin Panel.
"""
import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Database configuration
DB_NAME = os.getenv("MONGODB_DATABASE", "xumotjbot")
# Use MONGO_URI if provided, otherwise construct it from components
if os.getenv("MONGO_URI"):
    MONGO_URI = f"{os.getenv('MONGO_URI')}"
else:
    DB_HOST = os.getenv("MONGODB_HOST", "localhost")
    DB_PORT = os.getenv("MONGODB_PORT", "27017")
    DB_USER = os.getenv("MONGODB_USERNAME", "")
    DB_PASS = os.getenv("MONGODB_PASSWORD", "")
    
    if DB_USER and DB_PASS:
        MONGO_URI = f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        MONGO_URI = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Authentication configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Admin panel configuration
ADMIN_TITLE = "XumotjBot Admin Panel"
ADMIN_BASE_URL = os.getenv("ADMIN_BASE_URL", "/admin")

# Bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
CHANNEL_ID = os.getenv("CHANNEL_ID")