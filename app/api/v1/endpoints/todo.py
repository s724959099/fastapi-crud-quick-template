"""Todo api"""
from fastapi import APIRouter, HTTPException, Depends
from db import schemas, models
from pony.orm import flush
from api.deps import get_pagination_schema, Pagination

router = APIRouter()


@router.post(
    '/todo',
    name='Create one',
    response_model=schemas.Todo,
)
async def post_group(
        todo_create: schemas.TodoCreate
):
    ret = models.Todo(**todo_create.dict())
    flush()
    return ret


@router.put(
    '/todo/{item_id}',
    name='Update one',
    response_model=schemas.Todo,
)
async def post_group(
        todo_create: schemas.TodoCreate,
        item_id: int,
):
    todo = models.Todo.get(item_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Not Found')
    data = todo_create.dict()
    for field, value in data.items():
        setattr(todo, field, value)
    flush()
    return todo


@router.delete(
    '/todo/{item_id}',
    name='Delete one',
    status_code=204
)
async def post_group(
        item_id: int,
):
    todo = models.Todo.get(item_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Not Found')
    todo.delete()
    return


@router.get(
    '/todo/{item_id}',
    name='Get one',
    response_model=schemas.Todo,
)
async def post_group(
        item_id: int,
):
    todo = models.Todo.get(item_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Not Found')
    return todo


@router.get(
    '/todo',
    name='Get all',
    response_model=get_pagination_schema(schemas.Todo),
)
async def post_group(
        pagination: Pagination = Depends()
):
    query = models.Todo.select()
    return await pagination.paginate(query)
