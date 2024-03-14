from dataclasses import dataclass
from typing import List, Tuple, Union, Protocol


class Func(Protocol):
    async def __call__(self, jineng, myinfo, diinfo, myzhuangtai, dizhuangtai, changdi, **kwargs):
        ...


@dataclass
class Jinengfunc:
    keywords: Tuple[str, ...]
    func: Func
