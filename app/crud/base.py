"""Base crud"""
import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from db import models
from fastapi import HTTPException
from pony.orm import flush
from pony.orm.core import Query, desc
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

    def query(self) -> Query:
        """query data"""
        return self.model.select(lambda x: not x.deleted)

    @staticmethod
    def query_to_remove(query: Query):
        """find to remove"""
        obj = {
            'deleted': True,
            'deleted_at': datetime.datetime.now()
        }
        for el in query:
            # pylint:disable-next=consider-using-dict-items
            for key in obj:
                setattr(el, key, obj[key])

    @staticmethod
    def query_to_update(query: Query, obj=None):
        """find to update"""
        # auto update
        if obj is None:
            obj = {}
        obj.update({
            'deleted': False,
            'deleted_at': None,
            'updated_at': datetime.datetime.now()
        })
        for el in query:
            # set obj key
            for key in obj:
                setattr(el, key, obj[key])

    def get(self, _id: Any) -> Optional[ModelType]:
        """get data by id"""
        ret = self.model.get(id=_id, deleted=False)
        if not ret:
            raise HTTPException(status_code=404, detail='Not found')
        return ret

    def get_list_query(
            self,
    ) -> List[ModelType]:
        """get data by query"""
        return self.query().order_by(desc(self.model.created_at))

    def create(self, obj_in: Union[CreateSchemaType, dict],
               **kwargs) -> ModelType:
        """Create data"""
        obj_in_data = obj_in
        if isinstance(obj_in, BaseModel):
            obj_in_data = obj_in.dict()
        obj_in_data.update(kwargs)
        db_obj = self.model(**obj_in_data)  # type: ignore
        flush()
        return db_obj

    def update(
            self,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]],
            **kwargs
    ) -> ModelType:
        """update data"""
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict(exclude_unset=True)
        obj_in_data.update(kwargs)
        for field in obj_in_data:
            setattr(db_obj, field, obj_in_data[field])
        for field, val in kwargs.items():
            setattr(db_obj, field, val)
        db_obj.updated_at = datetime.datetime.now()
        flush()
        return db_obj

    def remove(self, _id: Optional[int] = None,
               obj: Optional[ModelType] = None, **kwargs) -> ModelType:
        """remove data"""
        if obj is None:
            obj = self.get(_id)
        if not obj:
            raise HTTPException(status_code=404, detail='Not found')
        # soft delete
        obj.deleted = True
        now = datetime.datetime.now()
        obj.deleted_at = now
        obj.updated_at = now
        for key, val in kwargs.items():
            setattr(obj, key, val)
        flush()
        return {
            'msg': 'success'
        }
