from fastapi import APIRouter

from app.api.routers.chat import router as chat_router
from app.api.routers.health import router as health_router
from app.api.routers.knowledge import router as knowledge_router
from app.core.constants import API_PREFIX

api_router = APIRouter(prefix=API_PREFIX)

api_router.include_router(health_router)
api_router.include_router(knowledge_router)
api_router.include_router(chat_router)
