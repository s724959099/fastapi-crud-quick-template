"""pony to BaseModel"""
from typing import List, Type, TypeVar

from pony.orm.core import EntityMeta
from pydantic import BaseModel, Field, create_model

ModelType = TypeVar('ModelType')


class OrmConfig:
    orm_mode = True


def pony_orm_to_pydantic(
        db_model: ModelType,
        class_name: str = None,
        field_parameter: dict = None,
        config: Type = OrmConfig,
        is_orm: bool = True,
        exclude: List[str] = None,
        include: dict = None,
) -> BaseModel:
    if field_parameter is None:
        field_parameter = {}
    if include is None:
        include = {}
    if exclude is None:
        exclude = []
    if not is_orm and config is OrmConfig:
        config = None
    fields = {}
    for column in db_model._attrs_:  # ignore: protected-access
        python_type = (
            include[column.name]
            if column.name in include else
            column.py_type
        )

        if isinstance(python_type, EntityMeta) or column.name in exclude:
            continue
        assert python_type, f'Could not infer python_type for {column}'

        default = None
        if column.default is None and not column.nullable:
            default = ...
        parameters = field_parameter.get(column.name, {})
        fields[column.name] = (python_type, Field(default, **parameters))

    exclude_str = '_exclude_' + '_'.join(exclude) if exclude else ''
    _class_name = f'{db_model.__name__}{"ORM" if is_orm else ""}{exclude_str}'
    class_name = class_name or _class_name
    pydantic_model = create_model(
        class_name, __config__=config, **fields
    )
    return pydantic_model
