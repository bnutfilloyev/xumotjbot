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
from views import NominationView
from database import Nomination

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
        Middleware(SessionMiddleware, secret_key=SECRET_KEY),
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
    _app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    # Get starlette_admin version to use proper parameter name
    import starlette_admin
    admin_version = getattr(starlette_admin, "__version__", "0.0.0")
    
    # Configure admin interface with proper static file parameters based on version
    admin_kwargs = {
        "title": ADMIN_TITLE,
        "base_url": ADMIN_BASE_URL,
        "auth_provider": AdminAuthProvider(),
    }
    
    # Different versions of starlette_admin use different parameter names
    if tuple(map(int, admin_version.split("."))) >= (0, 9, 0):
        # Version 0.9.0+ uses statics_dir
        admin_kwargs["statics_dir"] = STATIC_DIR
    else:
        # Older versions use static_files_dir
        admin_kwargs["static_files_dir"] = STATIC_DIR
        admin_kwargs["statics_url"] = "/static"
    
    _admin = Admin(**admin_kwargs)
    
    # Register models
    _admin.add_view(NominationView(Nomination, label="Nominations", icon="fa fa-star"))
    
    # Mount admin interface to app
    _admin.mount_to(_app)
    
    return _app


# Initialize application
app = create_app()
