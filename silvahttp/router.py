import inspect
from typing import Awaitable, Any, Callable, Optional

import msgspec
from starlette.requests import Headers, QueryParams
from starlette.exceptions import HTTPException
from starlette.status import HTTP_405_METHOD_NOT_ALLOWED

from silvanus.routing.simple import SimpleRouter
from silvanus.strategy.routers import FirstTrueRouterIterator
from silvanus.structures import RoutingData
from silvanus.integration.http import get_path_filters, parse_path
from silvahttp.enums import Methods, nothing


class Router:
    __slots__ = ("inner_router",)
    def __init__(self):
        self.inner_router = SimpleRouter()

    @staticmethod
    def _get_parameters_by_function(func: Any) -> Any:
        return {
            key: value.annotation for
            key, value in
            inspect.signature(func).parameters.items()
        }

    @staticmethod
    def _get_default_args(func) -> dict[str, Any]:
        signature = inspect.signature(func)
        return {
            k: v.default
            for k, v in signature.parameters.items()
            if v.default is not inspect.Parameter.empty
        }


    def add_method(
            self,
            method: Methods,
            path: str, func: Callable[[...], Awaitable[Any]]
    ) -> None:
        self.inner_router.add_router(
            SimpleRouter(
                filters=get_path_filters(
                    path=path,
                    param_types=self._get_parameters_by_function(func),
                    method=method
                ),
                data=self._get_pathed_method(func),
                parent=self.inner_router
            )
        )

    @staticmethod
    def _build_method_structures(data: dict[str, Any]) -> Any:
        return msgspec.defstruct(
            "MethodParameters",
            data.items()
        )

    def _get_pathed_method(
            self, func: Callable[[...], Awaitable[Any]]
    ) -> Callable[[...], Awaitable[Any]]:
        parameters = self._get_parameters_by_function(func)

        body_ = parameters.get("body", None)
        data_ = parameters.get("silva_data", None)

        headers_ = parameters.get("headers", None)

        if body_:
            parameters.pop("body")

        if data_:
            parameters.pop("silva_data")

        method_dataclass = self._build_method_structures(
            {
                **parameters
            }
        )

        defaults = self._get_default_args(func)

        async def wrapped(data: RoutingData):
            params: dict = data.request_data["method_params"]
            params.update(data.filters_data)

            if defaults:
                params.update(defaults)

            model = msgspec.convert(
                params,
                type=method_dataclass,
                strict=False
            )

            request = {}

            if headers_:
                request["headers"] = data.request_data["headers"]

            if data_:
                request["silva_data"] = data
                parameters["silva_data"] = data_

            request.update(
                msgspec.structs.asdict(model)
            )

            if body_:
                parameters["body"] = body_

                request["body"] = msgspec.json.decode(
                    data.request_data["body"],
                    type=body_,
                    strict=False
                )

            paramkeys = parameters.keys()
            return await func(
                **{key: value for key, value in request.items()
                   if key in paramkeys}
            )

        return wrapped


    def get(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.GET,
                path,
                func
            )

            return func

        return wrapper

    def post(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.POST,
                path,
                func
            )

            return func

        return wrapper

    def put(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.PUT,
                path,
                func
            )

            return func

        return wrapper

    def delete(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.DELETE,
                path,
                func
            )

            return func

        return wrapper

    def patch(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.PATCH,
                path,
                func
            )

            return func

        return wrapper

    def head(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.HEAD,
                path,
                func
            )

            return func

        return wrapper


    def trace(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.TRACE,
                path,
                func
            )

            return func

        return wrapper

    def options(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.OPTIONS,
                path,
                func
            )

            return func

        return wrapper


    def connect(self, path: str):
        def wrapper(func):
            self.add_method(
                Methods.CONNECT,
                path,
                func
            )

            return func

        return wrapper

    def add_router(self, router: "Router") -> None:
        self.inner_router.add_router(router.inner_router)

    def add_routers(self, *routers: "Router") -> None:
        inner_routers = [outer_router.inner_router for outer_router in routers]

        self.inner_router.add_routers(inner_routers)

    async def route(
            self,
            method: str,
            path: str,
            headers: Headers,
            query: QueryParams,
            body: Optional[str],
            app_data: dict[str, Any]
    ) -> Callable[[...], Awaitable[Any]] | None:

        data = parse_path(
            path=path,
            app_data=app_data,
            method=method
        )

        data.request_data["method_params"] = {
            **query
        }
        data.request_data["body"] = body

        data.request_data["headers"] = headers

        result = await self.inner_router.route(
            data,
            iterator=FirstTrueRouterIterator(on_nothing=nothing)
        )

        if result is nothing:
            raise HTTPException(
                status_code=HTTP_405_METHOD_NOT_ALLOWED,
                detail="access denied or method not found"
            )

        return await result(data)
