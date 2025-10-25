from dataclasses import dataclass, astuple

from silvahttp import Silva, Router

app = Silva()

router = Router()
app.include_router(router)


@dataclass()
class Some:
    number: int
    data: str
    age: int | None


@router.get("/some/{number}/{data}")
async def some_get(number: int, data: str, age: int | None = None) -> Some:
    return Some(number, data, age)


@router.post("/some")
async def some_post(body: Some) -> tuple[int, str, int]:
    return astuple(body)
