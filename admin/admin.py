"""
XumotjBot Admin Panel
Provides administrative interface for managing bot data.
"""
import logging
import os
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.mongoengine import Admin

from auth import AdminAuth, AdminAuthProvider, LoginRequiredMiddleware
from config import SECRET_KEY, DEBUG, ADMIN_TITLE, ADMIN_BASE_URL
from db import get_startup_handlers, get_shutdown_handlers
from views import NominationView, UserView, VoteView
from database import Nomination, User, Vote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("xumotjbot.admin")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)


def create_app() -> Starlette:
    """Create and configure the Starlette application."""
    middleware = [
        Middleware(SessionMiddleware, secret_key=SECRET_KEY, https_only=False),
        Middleware(AuthenticationMiddleware, backend=AdminAuth()),
        Middleware(LoginRequiredMiddleware),
    ]
    
    _app = Starlette(
        on_startup=get_startup_handlers(),
        on_shutdown=get_shutdown_handlers(),
        debug=DEBUG,
        middleware=middleware,
    )
    
    # Mount static files directly
    _app.mount("/static", StaticFiles(directory="static"), name="static")   

    # Configure admin interface with proper static file parameters based on version
    admin_kwargs = {
        "title": ADMIN_TITLE,
        "base_url": ADMIN_BASE_URL,
        "auth_provider": AdminAuthProvider(),
        "statics_dir": STATIC_DIR,
    }
    
    _admin = Admin(**admin_kwargs)
    
    # Register models
    _admin.add_view(NominationView(Nomination, label="Nominations", icon="fa fa-star"))
    _admin.add_view(UserView(User, label="Users", icon="fa fa-users"))
    _admin.add_view(VoteView(Vote, label="Votes", icon="fa fa-check-square"))
    
    # Mount admin interface to app
    _admin.mount_to(_app)
    
    return _app


# Initialize application
app = create_app()
