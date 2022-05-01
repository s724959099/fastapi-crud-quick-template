"""deps module"""
import typing
from typing import List, Optional
from fastapi import Query, Request
from pydantic import BaseModel, Field


def get_pagination_schema(
        schema: Optional[typing.Type[typing.Any]] = None
) -> typing.Union[type, BaseModel]:
    """

    Args:
        schema:

    Returns:
        Pagination Schmea

    """

    class PageModel(BaseModel):
        """page model"""
        count: int = Field(..., description='filter後的資料總數目')
        next: Optional[str] = Field(None, description='下一頁的網址，如果不是最後一頁的話')
        previous: Optional[str] = Field(None, description='下一頁的網址，如果不是最後一頁的話')
        data: List[schema] = Field(...,
                                   description=f'{schema.__name__} 的List 結果')

    class_ = type(f'{schema.__name__}Page', (PageModel,), {})

    return class_


class Pagination:
    """
    from fastapi conrtib to get it
    i fix some code which only can fit to mongo
    ----

    Query params parser and db collection paginator in one.

    Use it as dependency in route, then invoke `paginate` with serializer:

    .. code-block:: python

        app = FastAPI()

        class SomeSerializer(ModelSerializer):
            class Meta:
                model = SomeModel

        @app.get("/")
        async def list(pagination: Pagination = Depends()):
            filter_kwargs = {}
            return await pagination.paginate(
                serializer_class=SomeSerializer, **filter_kwargs
            )

    Subclass this pagination to define custom
    default & maximum values for offset & limit:

    .. code-block:: python

        class CustomPagination(Pagination):
            default_offset = 90
            default_limit = 1
            max_offset = 100`
            max_limit = 2000

    :param request: starlette Request object
    :param offset: query param of how many records to skip
    :param limit: query param of how many records to show
    """

    default_offset = 0
    default_limit = 10
    max_offset = None
    max_limit = 100

    def __init__(
            self,
            request: Request,
            offset: int = Query(default=default_offset, ge=0, le=max_offset),
            limit: int = Query(default=default_limit, ge=1, le=max_limit),
    ):
        self.request = request
        self.offset = offset
        self.limit = limit
        self.model = None
        self.count = None
        self.list = []

    async def get_count(self, **kwargs) -> int:
        """
        Retrieves counts for query list, filtered by kwargs.

        :param kwargs: filters that are proxied in db query
        :return: number of found records
        """
        self.count = await self.model.count(**kwargs)
        return self.count

    def get_next_url(self) -> typing.Optional[str]:
        """
        Constructs `next` parameter in resulting JSON,
        produces URL for next "page" of paginated results.

        :return: URL for next "page" of paginated results.
        """
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.include_query_params(
                limit=self.limit, offset=self.offset + self.limit
            )
        )

    def get_previous_url(self) -> typing.Optional[str]:
        """
        Constructs `previous` parameter in resulting JSON,
        produces URL for previous "page" of paginated results.

        :return: URL for previous "page" of paginated results.
        """
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return str(self.request.url.remove_query_params(keys=['offset']))

        return str(
            self.request.url.include_query_params(
                limit=self.limit, offset=self.offset - self.limit
            )
        )

    async def paginate(
            self,
            query: Query
    ) -> dict:
        """
        Actual pagination function, takes serializer class,
        filter options as kwargs and returns dict with the following fields:
            * count - counts for query list, filtered by kwargs
            * next - URL for next "page" of paginated results
            * previous - URL for previous "page" of paginated results
            * result - actual list of records (dicts)

        :param query:
        :return: dict that should be returned as a response
        """
        self.count = query.count()
        return {
            'count': self.count,
            'next': self.get_next_url(),
            'previous': self.get_previous_url(),
            'data': query.limit(self.limit, offset=self.offset)[:],
        }
