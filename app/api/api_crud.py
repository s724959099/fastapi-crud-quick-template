from crud.base import CRUDBase
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from api.deps import Pagination, get_pagination_schema
import typing


class RouterAbstract:
    def __init__(self, crud_api: CRUDBase):
        self._crud = crud_api

    async def get_one(self, *args, **kwargs):
        pass

    async def get_all(
            self,
            *args, **kwargs
    ):
        pass

    async def put_one(
            self,
            *args, **kwargs
    ):
        pass

    async def post_one(
            self,
            *args, **kwargs
    ):
        pass

    async def delete_one(self, *args, **kwargs):
        pass


def add_crud_route_factory(
        router: APIRouter,
        crud: CRUDBase,
        create_schema: BaseModel,
        update_schema: BaseModel,
        response_model: typing.Optional[typing.Type[typing.Any]] = None,
        path_suffix: str = '/',
        router_method_class: typing.Optional[RouterAbstract] = None,
        # id_field_name: str = 'item_id',
        get_one_route: bool = True,
        get_all_route: bool = True,
        put_one_route: bool = True,
        post_one_route: bool = True,
        delete_one_route: bool = True,
):
    """
    主要功能寫在 crud
    並透過：
    get_one_route
    get_all_route
    put_one_route
    post_one_route
    delete_one_route
    判斷是否需要開啟 該 CRUD
    schema 也可以客製
    """

    class RouterMethod(RouterAbstract):

        async def get_one(self, item_id: typing.Any):
            return self._crud.get(item_id)

        async def get_all(
                self,
                pagination: Pagination = Depends()
        ):
            query = self._crud.query()
            return await pagination.paginate(query)

        async def put_one(
                self,
                item_id: typing.Any,
                _update_schema: update_schema
        ):
            return self._crud.update_by_id(item_id, _update_schema)

        async def post_one(
                self,
                _create_schema: create_schema
        ):
            return self._crud.create(_create_schema)

        async def delete_one(self, item_id: typing.Any):
            return self._crud.remove_by_id(item_id)

    _RouterMethodClass = router_method_class or RouterMethod
    router_method_instance = _RouterMethodClass(crud)
    if get_all_route:
        router.add_api_route(
            f'{path_suffix}',
            router_method_instance.get_all,
            name='Get All',
            response_model=get_pagination_schema(response_model),
            methods=['GET']
        )
    if get_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method_instance.get_one,
            name='Get One',
            response_model=response_model,
            methods=['GET']
        )
    if post_one_route:
        router.add_api_route(
            f'{path_suffix}',
            router_method_instance.post_one,
            name='Post One',
            response_model=response_model,
            methods=['POST']
        )
    if put_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method_instance.put_one,
            name='Put One',
            response_model=response_model,
            methods=['PUT']
        )
    if delete_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method_instance.delete_one,
            name='Delete One',
            methods=['DELETE'],
            status_code=204
        )
