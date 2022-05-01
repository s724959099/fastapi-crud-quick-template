"""Base crud"""
import typing
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from db import models
from fastapi import HTTPException
from pony.orm import flush
from pony.orm.core import Query
from pydantic import BaseModel

ModelType = TypeVar('ModelType', bound=models.db.Entity)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD base class"""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def query(self, *args, **kwargs) -> Query:
        """query data"""
        return self.model.select(*args, **kwargs)

    def update_by_query(
            self,
            query: Query,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            exclude: Optional[typing.List] = None,
            extra_data: Optional[dict] = None,
    ):
        for db_obj in query:
            self.update_obj(db_obj, data, exclude, extra_data)
        flush()

    def get(
            self, _id: Any,
            extra_query: Optional[dict] = None
    ) -> Optional[ModelType]:
        """get data by id"""
        extra_query = extra_query or {}
        ret = self.model.get(id=_id, **extra_query)
        if not ret:
            raise HTTPException(status_code=404, detail='Not found')
        return ret

    def get_query_list(
            self,
    ) -> List[ModelType]:
        """get list data by query"""
        return list(self.query())

    def create(self,
               data: Union[CreateSchemaType, Dict[str, Any]],
               exclude: Optional[typing.List] = None,
               extra_data: Optional[dict] = None) -> ModelType:
        """Create data"""
        if isinstance(data, BaseModel):
            data = data.dict()
        db_obj = self.model(**data)
        db_obj = self.update_obj(db_obj, {}, exclude, extra_data)
        flush()
        return db_obj

    def update_by_id(
            self,
            _id: Any,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            exclude: Optional[typing.List] = None,
            extra_data: Optional[dict] = None,
    ):

        db_obj = self.get(_id)
        return self.update_by_db_object(db_obj, data, exclude, extra_data)

    @staticmethod
    def update_obj(
            db_obj: ModelType,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            exclude: Optional[typing.List] = None,
            extra_data: Optional[dict] = None,
    ):
        exclude = exclude or []
        extra_data = extra_data or {}
        # check if data is not dict
        if isinstance(data, BaseModel):
            data = data.dict()
        # udpate by data
        for field, value in data.items():
            if field in exclude:
                continue
            setattr(db_obj, field, value)
        for field, value in extra_data:
            if field in exclude:
                continue
            setattr(db_obj, field, value)
        return db_obj

    def update_by_db_object(
            self,
            db_obj: ModelType,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            exclude: Optional[typing.List] = None,
            extra_data: Optional[dict] = None,
    ):
        """db data by db object"""
        db_obj = self.update_obj(db_obj, data, exclude, extra_data)
        flush()
        return db_obj

    def remove_by_id(self, _id: Any):
        """remove data by id"""
        db_obj = self.get(_id)
        db_obj.delete()
        flush()

    @staticmethod
    def remove_by_query(
            query: Query
    ):
        query.delete()
        flush()
