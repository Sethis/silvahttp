from typing import Any, Optional

import msgspec
from starlette.requests import Request, Headers, QueryParams
from starlette.responses import Response, JSONResponse, PlainTextResponse

from silvahttp.router import Router
from silvahttp.enums import Methods
from silvahttp.default_router import default_router


class Silva:
    __slots__ = ("_router", "_app_data")
    def __init__(self, **data) -> None:
        self._router = Router()
        self._router.add_router(default_router)

        self._app_data = data

    def include_router(self, router: Router) -> None:
        self._router.add_router(router)

    def include_routers(self, *routers: Router) -> None:
        self._router.add_routers(*routers)

    async def _route(
            self,
            method: str,
            path: str,
            headers: Headers,
            query_params: QueryParams,
            app_data: dict[str, Any],
            body: Optional[str] = None
    ) -> Response:

        response = await self._router.route(
            method=method,
            path=path,
            headers=headers,
            query=query_params,
            body=body,
            app_data=app_data
        )

        if isinstance(response, str):
            return PlainTextResponse(response)

        result = msgspec.json.encode(response)

        return JSONResponse(
            result.decode()
        )

    @staticmethod
    async def _get_body(request: Request) -> str | None:
        if not request.method in {
            Methods.GET,
            Methods.HEAD,
            Methods.DELETE,
            Methods.OPTIONS,
            Methods.TRACE
        }:
            result = await request.body()

            return result.decode()

        else:
            return None

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        assert scope['type'] == 'http'

        request = Request(scope, receive)
        body = await self._get_body(request)

        response = await self._route(
            method=request.method,
            path=request.url.path,
            headers=request.headers,
            query_params=request.query_params,
            body=body,
            app_data=self._app_data
        )

        await response(scope, receive, send)
