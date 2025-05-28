from collections.abc import Callable, Mapping
from itertools import product

import pytest
from cosy.dsl import DSL
from cosy.synthesizer import Specification, Synthesizer
from cosy.types import Constructor, Literal, Type, Var


def plus_one(a: str) -> Callable[[Mapping[str, Literal]], int]:
    def _inner(vs: Mapping[str, Literal]) -> int:
        return int(1 + vs[a].value)

    return _inner


def is_free(pos: tuple[int, int]) -> bool:
    col, row = pos
    seed = 0
    if row == col:
        return True
    return pow(11, (row + col + seed) * (row + col + seed) + col + 7, 1000003) % 5 > 0


@pytest.fixture
def component_specifications() -> (
    Mapping[
        Callable[[int, str], str] | str,
        Specification,
    ]
):
    def up(b: int, p: str) -> str:
        return f"{p} => UP({b})"

    def down(b: int, p: str) -> str:
        return f"{p} => DOWN({b})"

    def left(b: int, p: str) -> str:
        return f"{p} => LEFT({b})"

    def right(b: int, p: str) -> str:
        return f"{p} => RIGHT({b})"

    def pos(ab: str) -> Type:
        return Constructor("pos", Var(ab))

    return {
        up: DSL()
        .parameter("b", "int2")
        .parameter("a", "int2", lambda vs: [(vs["b"][0], vs["b"][1] + 1)])
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        down: DSL()
        .parameter("b", "int2")
        .parameter("a", "int2", lambda vs: [(vs["b"][0], vs["b"][1] - 1)])
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        left: DSL()
        .parameter("b", "int2")
        .parameter("a", "int2", lambda vs: [(vs["b"][0] + 1, vs["b"][1])])
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        right: DSL()
        .parameter("b", "int2")
        .parameter("a", "int2", lambda vs: [(vs["b"][0] - 1, vs["b"][1])])
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        "START": "pos" @ (Literal((0, 0), "int2")),
    }


@pytest.fixture
def literals():
    return {"int2": frozenset(filter(is_free, product(range(400), range(400))))}


def test_benchmark_maze(component_specifications, literals, benchmark):
    fin = "pos" @ (Literal((400 - 1, 400 - 1), "int2"))

    synthesizer = Synthesizer(component_specifications, literals)
    benchmark(synthesizer.construct_solution_space, fin)
