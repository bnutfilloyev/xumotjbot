import logging
from dataclasses import dataclass, field

from environs import Env

env = Env()
env.read_env()


@dataclass
class BotConfig:
    """Bot configuration."""
    token: str = env.str("TELEGRAM_TOKEN")
    admins: list = field(default_factory=lambda: env.list("ADMIN_IDS"))
    debug: bool = env.bool("DEBUG", False)
    channel_id: str = env.str("CHANNEL_ID")


@dataclass
class MongoDBConfig:
    """MongoDB configuration."""
    host: str = env.str("MONGODB_HOST", "localhost")
    port: int = env.int("MONGODB_PORT", 27017)
    username: str = env.str("MONGODB_USERNAME", "")
    password: str = env.str("MONGODB_PASSWORD", "")
    database: str = env.str("MONGODB_DATABASE", "xumotjbot")
    
    @property
    def uri(self):
        """Generate MongoDB URI from components or use direct URI if provided"""
        if env.str("MONGO_URI", ""):
            return env.str("MONGO_URI")
        
        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"mongodb://{auth}{self.host}:{self.port}/{self.database}"


@dataclass
class AdminConfig:
    """Admin panel configuration."""
    username: str = env.str("ADMIN_USERNAME", "admin")
    password: str = env.str("ADMIN_PASSWORD", "admin")
    secret_key: str = env.str("SECRET_KEY", "default_secret_key")
    host: str = env.str("HOST", "127.0.0.1")
    port: int = env.int("PORT", 8000)
    base_url: str = env.str("ADMIN_BASE_URL", "/admin")


@dataclass
class Configuration:
    """All in one configuration's class."""
    bot = BotConfig()
    db = MongoDBConfig()
    admin = AdminConfig()


conf = Configuration()