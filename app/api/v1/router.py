"""api router"""
from api.v1.endpoints import user, todo
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(todo.router)
