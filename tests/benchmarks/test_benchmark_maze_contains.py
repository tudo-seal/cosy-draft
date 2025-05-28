from collections.abc import Callable, Container, Mapping

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
        Callable[[int, int, str], str] | str,
        Specification,
    ]
):
    def up(b: int, _: int, p: str) -> str:
        return f"{p} => UP({b})"

    def down(b: int, _: int, p: str) -> str:
        return f"{p} => DOWN({b})"

    def left(b: int, _: int, p: str) -> str:
        return f"{p} => LEFT({b})"

    def right(b: int, _: int, p: str) -> str:
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


class Pos(Container):
    # represents the set of all free positions
    def __contains__(self, value: object) -> bool:
        if isinstance(value, tuple):
            x, y = value
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < 150 and 0 <= y < 150 and is_free((x, y)):
                return True
        return False


@pytest.fixture
def literals():
    return {"int2": Pos()}


@pytest.fixture
def fin():
    return "pos" @ (Literal((150 - 1, 150 - 1), "int2"))


def test_benchmark_maze_contains(component_specifications, literals, benchmark):
    synthesizer = Synthesizer(component_specifications, literals)
    benchmark(synthesizer.construct_solution_space, fin)
