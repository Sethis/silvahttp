A simple example of using the **[silvanus](https://github.com/Sethis/silvanus)** routing 
library to create a high-level http asgi framework

```python
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
async def some_get(number: int, data: str, age: int | None) -> Some:
    return Some(number, data, age)


@router.post("/some")
async def some_post(body: Some) -> tuple[int, str, int]:
    return astuple(body)

```


**Attention**: at the moment, this is more an example of how 
you can build the simplest library possible on top of low-level 
silvanus. Right now, this solution is clearly 
not production-ready, but it may be interesting to explore.