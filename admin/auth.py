"""
Authentication providers for the XumotjBot Admin Panel.
"""
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_admin.auth import AdminUser, AuthProvider

from config import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_TITLE


class AdminAuth(AuthenticationBackend):
    """Starlette authentication backend for the admin panel."""
    
    async def authenticate(self, request):
        if "user" not in request.session:
            return None
        
        user = request.session["user"]
        return AuthCredentials(["authenticated"]), SimpleUser(user["username"])


class AdminAuthProvider(AuthProvider):
    """Authentication provider for the admin interface."""
    
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        """Process login request."""
        # Check if credentials match
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Save username in session
            request.session.update({"user": {"username": username}})
            return response
        
        # If authentication fails, raise LoginFailed exception
        from starlette_admin.exceptions import LoginFailed
        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        """Check if user is authenticated."""
        if "user" in request.session:
            # Save current user in request state
            request.state.user = request.session["user"]
            return True
        return False

    def get_admin_config(self, request: Request):
        """Get admin configuration."""
        from starlette_admin.auth import AdminConfig
        return AdminConfig(
            app_title=ADMIN_TITLE,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        """Get current admin user."""
        user = request.state.user
        # The AdminUser class only accepts username and photo_url
        return AdminUser(
            username=user["username"],
            photo_url=None  # Optional photo URL can be set if available
        )

    async def logout(self, request: Request, response: Response) -> Response:
        """Process logout request."""
        request.session.clear()
        return response


class LoginRequiredMiddleware:
    """Middleware to check if user is authenticated."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        
        if request.url.path.startswith("/admin"):
            if "user" not in request.session and not request.url.path.endswith("/login"):
                redirect_url = request.url.replace(path="/admin/login", query="").replace(scheme="https")
                response = RedirectResponse(url=str(redirect_url), status_code=302)
                await response(scope, receive, send)
                return
                
        await self.app(scope, receive, send)
