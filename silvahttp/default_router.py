from silvahttp.router import Router

default_router = Router()

@default_router.get("/favicon.ico")
async def icon() -> str:
    return ""
