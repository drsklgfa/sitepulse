from fastapi import APIRouter

from app.api.routes import auth, dashboard, monitors, notifications, runs, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(monitors.router)
api_router.include_router(runs.router)
api_router.include_router(notifications.router)
