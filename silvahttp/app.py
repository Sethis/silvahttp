from typing import Any, Optional

import msgspec
from starlette.requests import Request, Headers, QueryParams
from starlette.responses import Response, JSONResponse, PlainTextResponse

from silvahttp.router import Router


class Silva:
    def __init__(self, **data) -> None:
        self._router = Router()
        self.app_data = data

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

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        assert scope['type'] == 'http'
        request = Request(scope, receive)

        if not request.method in {"GET", "HEAD", "DELETE", "OPTIONS", "TRACE"}:
            body = await request.body()
        else:
            body = None

        if "ico" in request.url.path:
            response = PlainTextResponse("OK")

        else:
            response = await self._route(
                method=request.method,
                path=request.url.path,
                headers=request.headers,
                query_params=request.query_params,
                body=body,
                app_data=self.app_data
            )

        await response(scope, receive, send)
