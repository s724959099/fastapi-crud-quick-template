"""Todo api"""
from fastapi import APIRouter
from db import schemas, models
from crud import base
from api.api_crud import add_crud_route_factory

crud = base.CRUDBase(models.Todo)
router = APIRouter(
    prefix='/todo',
    tags=['todo']
)

add_crud_route_factory(
    router=router,
    crud=crud,
    create_schema=schemas.TodoCreate,
    update_schema=schemas.TodoUpdate,
    response_model=schemas.Todo,
    path_suffix=''
)
