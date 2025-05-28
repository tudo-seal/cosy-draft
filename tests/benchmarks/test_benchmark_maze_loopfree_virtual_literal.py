from collections.abc import Callable, Container, Iterable, Mapping
from functools import partial
from itertools import chain, combinations, product
from typing import Any, cast

import pytest
from cosy.dsl import DSL
from cosy.synthesizer import ParameterSpace, Specification, Synthesizer
from cosy.tree import Tree
from cosy.types import Constructor, Literal, Type, Var


def start_str() -> str:
    return "START"


def visited(path: Tree[Any]) -> set[tuple[int, int]]:
    if path.root == start_str:
        return {(0, 0)}
    return {cast(tuple[int, int], path.parameters["a"].root)} | visited(path.parameters["pos"])


def powerset(s: list[tuple[int, int]]) -> list[frozenset[tuple[int, int]]]:
    return list(map(frozenset, chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))))


def is_free(size: int, pos: tuple[int, int]) -> bool:
    """
    Create a maze in the form:
    XXX...XXX
    X       X
    X X...X X
    . ..... .
    X X...X X
    X       X
    X X...XXX
    X       X
    XXX...XXX
    """

    col, row = pos
    if row in [0, size - 1, size - 3]:
        return True
    if row == size - 2 and col == size - 1:
        return False
    if col in [0, size - 1]:
        return True
    return False


@pytest.fixture
def component_specifications() -> (
    Mapping[
        Callable[..., str] | str,
        Specification,
    ]
):
    def up(_old_visited, b, _a, _new_visited, p) -> str:
        return f"{p} => UP({b})"

    def down(_old_visited, b, _a, _new_visited, p) -> str:
        return f"{p} => DOWN({b})"

    def left(_old_visited, b, _a, _new_visited, p) -> str:
        return f"{p} => LEFT({b})"

    def right(_old_visited, b, _a, _new_visited, p) -> str:
        return f"{p} => RIGHT({b})"

    def pos(ab: str) -> Type:
        return Constructor("pos", Var(ab))

    def vis(ab: str) -> Type:
        return Constructor("vis", Var(ab))

    return {
        up: DSL()
        .parameter("old_visited", "power_int2")
        .parameter("b", "int2")
        .parameter_constraint(lambda vs: vs["b"] not in vs["old_visited"])
        .parameter("a", "int2", lambda vs: [(vs["b"][0], vs["b"][1] + 1)])
        .parameter("new_visited", "power_int2", lambda vs: [vs["old_visited"] | {vs["b"]}])
        .argument("pos", pos("a") & vis("new_visited"))
        .suffix(pos("b") & vis("old_visited")),
        down: DSL()
        .parameter("old_visited", "power_int2")
        .parameter("b", "int2")
        .parameter_constraint(lambda vs: vs["b"] not in vs["old_visited"])
        .parameter("a", "int2", lambda vs: [(vs["b"][0], vs["b"][1] - 1)])
        .parameter("new_visited", "power_int2", lambda vs: [vs["old_visited"] | {vs["b"]}])
        .argument("pos", pos("a") & vis("new_visited"))
        .suffix(pos("b") & vis("old_visited")),
        left: DSL()
        .parameter("old_visited", "power_int2")
        .parameter("b", "int2")
        .parameter_constraint(lambda vs: vs["b"] not in vs["old_visited"])
        .parameter("a", "int2", lambda vs: [(vs["b"][0] + 1, vs["b"][1])])
        .parameter("new_visited", "power_int2", lambda vs: [vs["old_visited"] | {vs["b"]}])
        .argument("pos", pos("a") & vis("new_visited"))
        .suffix(pos("b") & vis("old_visited")),
        right: DSL()
        .parameter("old_visited", "power_int2")
        .parameter("b", "int2")
        .parameter_constraint(lambda vs: vs["b"] not in vs["old_visited"])
        .parameter("a", "int2", lambda vs: [(vs["b"][0] - 1, vs["b"][1])])
        .parameter("new_visited", "power_int2", lambda vs: [vs["old_visited"] | {vs["b"]}])
        .argument("pos", pos("a") & vis("new_visited"))
        .suffix(pos("b") & vis("old_visited")),
        start_str: DSL()
        .parameter("visited", "power_int2")
        .parameter_constraint(lambda vs: (0, 0) not in vs["visited"])
        .suffix("pos" @ (Literal((0, 0), "int2")) & vis("visited")),
    }


@pytest.fixture
def positions():
    return list(filter(partial(is_free, 2000), product(range(2000), range(2000))))


@pytest.fixture
def power_positions(positions):
    class Powerset(Container):
        def __init__(self, s: Iterable[tuple[int, int]]):
            self.s = s

        def __contains__(self, item: object) -> bool:
            if not isinstance(item, frozenset):
                return False
            return item.issubset(self.s)

    return Powerset(positions)


@pytest.fixture
def literals(positions, power_positions) -> ParameterSpace:
    return {"int2": positions, "power_int2": power_positions}


@pytest.fixture
def fin():
    return ("pos" @ (Literal((2000 - 1, 2000 - 1), "int2"))) & ("vis" @ Literal(frozenset(), "power_int2"))


def test_benchmark_maze_loopfree_virtual_literal(component_specifications, literals, fin, benchmark):
    synthesizer = Synthesizer(component_specifications, literals)
    benchmark(synthesizer.construct_solution_space, fin)
