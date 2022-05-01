from crud.base import CRUDBase
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from api.deps import Pagination, get_pagination_schema
import typing


def add_crud_route_factory(
        router: APIRouter,
        crud: CRUDBase,
        create_schema: BaseModel,
        update_schema: BaseModel,
        response_model: typing.Optional[typing.Type[typing.Any]] = None,
        path_suffix: str = '/',
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

    class RouterMethod:
        def __init__(self):
            self.crud = crud

        async def get_one(self, item_id: typing.Any):
            return self.crud.get(item_id)

        async def get_all(
                self,
                pagination: Pagination = Depends()
        ):
            query = self.crud.query()
            return await pagination.paginate(query)

        async def put_one(
                self,
                item_id: typing.Any,
                _update_schema: update_schema
        ):
            return self.crud.update_by_id(item_id, _update_schema)

        async def post_one(
                self,
                _create_schema: create_schema
        ):
            return self.crud.create(_create_schema)

        async def delete_one(self, item_id: typing.Any):
            return self.crud.remove_by_id(item_id)

    router_method = RouterMethod()
    if get_all_route:
        router.add_api_route(
            f'{path_suffix}',
            router_method.get_all,
            name='Get All',
            response_model=get_pagination_schema(response_model),
            methods=['GET']
        )
    if get_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method.get_one,
            name='Get One',
            response_model=response_model,
            methods=['GET']
        )
    if post_one_route:
        router.add_api_route(
            f'{path_suffix}',
            router_method.post_one,
            name='Post One',
            response_model=response_model,
            methods=['POST']
        )
    if put_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method.put_one,
            name='Put One',
            response_model=response_model,
            methods=['PUT']
        )
    if delete_one_route:
        router.add_api_route(
            f'/{{item_id}}{path_suffix}',
            router_method.delete_one,
            name='Delete One',
            methods=['DELETE'],
            status_code=204
        )
