"""Todo api"""
from fastapi import APIRouter, Depends
from db import schemas, models
from api.deps import get_pagination_schema, Pagination
from crud import base

crud = base.CRUDBase(models.Todo)
router = APIRouter()


@router.post(
    '/todo',
    name='Create one',
    response_model=schemas.Todo,
)
async def post_group(
        todo_create: schemas.TodoCreate
):
    return crud.create(todo_create)


@router.put(
    '/todo/{item_id}',
    name='Update one',
    response_model=schemas.Todo,
)
async def post_group(
        todo_create: schemas.TodoCreate,
        item_id: int,
):
    return crud.update_by_id(item_id, todo_create)


@router.delete(
    '/todo/{item_id}',
    name='Delete one',
    status_code=204
)
async def post_group(
        item_id: int,
):
    crud.remove_by_id(item_id)
    return


@router.get(
    '/todo/{item_id}',
    name='Get one',
    response_model=schemas.Todo,
)
async def post_group(
        item_id: int,
):
    return crud.get(item_id)


@router.get(
    '/todo',
    name='Get all',
    response_model=get_pagination_schema(schemas.Todo),
)
async def post_group(
        pagination: Pagination = Depends()
):
    query = crud.query()
    return await pagination.paginate(query)
