from dataclasses import dataclass, astuple

from silvahttp import Silva, Router
from silvanus.structures import RoutingData

app = Silva()

router = Router()
app.include_router(router)


@dataclass()
class Some:
    number: int
    data: str
    age: int | None


@router.get("/")
async def some_root() -> None:
    return None


@router.get("/some/{number}/{data}")
async def some_get(number: int, data: str, age: int | None = None) -> Some:
    return Some(number, data, age)


@router.post("/some")
async def some_post(body: Some) -> tuple[int, str, int]:
    return astuple(body)


@router.get("/stest/{number}")
async def some_silvatest(number: int, silva_data: RoutingData) -> str:
    return silva_data.__repr__()
