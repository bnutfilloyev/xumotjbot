from handlers.common import start_router
from handlers.registration import register_router
from handlers.broadcast import broadcast_router
from handlers.nomination import router as nomination_router

routers = (start_router, register_router, broadcast_router, nomination_router)