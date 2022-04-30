from db import models
from utils.pony_pydantic import pony_orm_to_pydantic
import typing

UserCreate = pony_orm_to_pydantic(models.User, exclude=['id'], is_orm=False)
TodoCreate = pony_orm_to_pydantic(models.Todo, exclude=['id'], is_orm=False)
User = pony_orm_to_pydantic(models.User)
Todo = pony_orm_to_pydantic(models.Todo)
TodoWithUser = pony_orm_to_pydantic(
    models.Todo,
    include={'user': User}
)
UserWithTodos = pony_orm_to_pydantic(
    models.User,
    include={'todos': typing.List[Todo]}
)
