from collections.abc import Callable, Container, Mapping

import pytest
from cosy.dsl import DSL
from cosy.synthesizer import Specification, Synthesizer
from cosy.types import Constructor, Literal, Type, Var


def is_free(pos: tuple[int, int]) -> bool:
    col, row = pos
    seed = 0
    if row == col:
        return True
    return pow(11, (row + col + seed) * (row + col + seed) + col + 7, 1000003) % 5 > 0


@pytest.fixture
def component_specifications() -> (
    Mapping[
        Callable[[tuple[int, int], tuple[int, int], str], str] | str,
        Specification,
    ]
):
    def up(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => UP({b})"

    def down(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => DOWN({b})"

    def left(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
        return f"{p} => LEFT({b})"

    def right(b: tuple[int, int], _a: tuple[int, int], p: str) -> str:
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


SIZE = 50


class Pos(Container):
    # represents the set of all free positions
    def __contains__(self, value: object) -> bool:
        if isinstance(value, tuple):
            x, y = value
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < SIZE and 0 <= y < SIZE and is_free((x, y)):
                return True
        return False


@pytest.fixture
def literals():
    return {"int2": Pos()}


@pytest.fixture
def fin():
    return "pos" @ (Literal((SIZE - 1, SIZE - 1), "int2"))


def test_benchmark_maze_contains(component_specifications, literals, fin, benchmark):
    synthesizer = Synthesizer(component_specifications, literals)
    benchmark(synthesizer.construct_solution_space, fin)
