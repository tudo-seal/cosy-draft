from collections.abc import Callable, Iterable, Mapping
from itertools import product
from typing import Any

import pytest
from cosy.dsl import DSL
from cosy.synthesizer import Specification, Synthesizer
from cosy.tree import Tree
from cosy.types import Constructor, Literal, Type, Var


def is_free(pos: tuple[int, int]) -> bool:
    col, row = pos
    seed = 0
    if row == col:
        return True
    return pow(11, (row + col + seed) * (row + col + seed) + col + 7, 1000003) % 5 > 0


def getpath(path: Tree[Any]) -> Iterable[tuple[int, int]]:
    position_arg = path.parameters["b"].root
    while path.root != "START":
        if isinstance(position_arg, tuple):
            yield position_arg
        position_arg = path.parameters["a"].root
        path = path.parameters["pos"]


@pytest.fixture
def component_specifications() -> (
    Mapping[
        Callable[[int, int, str], str] | str,
        Specification,
    ]
):
    def up(_: int, b: int, p: str) -> str:
        return f"{p} => UP({b})"

    def down(_: int, b: int, p: str) -> str:
        return f"{p} => DOWN({b})"

    def left(_: int, b: int, p: str) -> str:
        return f"{p} => LEFT({b})"

    def right(_: int, b: int, p: str) -> str:
        return f"{p} => RIGHT({b})"

    def pos(ab: str) -> Type:
        return Constructor("pos", Var(ab))

    return {
        up: DSL()
        .parameter("a", "int2")
        .parameter("b", "int2", lambda vs: [(vs["a"][0], vs["a"][1] - 1)])
        .parameter_constraint(lambda vs: is_free(vs["b"]))
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        down: DSL()
        .parameter("a", "int2")
        .parameter("b", "int2", lambda vs: [(vs["a"][0], vs["a"][1] + 1)])
        .parameter_constraint(lambda vs: is_free(vs["b"]))
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        left: DSL()
        .parameter("a", "int2")
        .parameter("b", "int2", lambda vs: [(vs["a"][0] - 1, vs["a"][1])])
        .parameter_constraint(lambda vs: is_free(vs["b"]))
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        right: DSL()
        .parameter("a", "int2")
        .parameter("b", "int2", lambda vs: [(vs["a"][0] + 1, vs["a"][1])])
        .parameter_constraint(lambda vs: is_free(vs["b"]))
        .argument("pos", pos("a"))
        .suffix(pos("b")),
        "START": "pos" @ (Literal((0, 0), "int2")),
    }


@pytest.fixture
def literals():
    return {"int2": list(product(range(4), range(4)))}


@pytest.fixture
def fin():
    return "pos" @ (Literal((4 - 1, 4 - 1), "int2"))


def test_benchmark_labyrinth_clsp_no_loop_generate_and_test(component_specifications, literals, fin, benchmark):
    synthesizer = Synthesizer(component_specifications, parameter_space=literals)

    def synthesize_and_enumerate():
        grammar = synthesizer.construct_solution_space(fin)

        for tree in grammar.enumerate_trees(fin, 10000):
            positions = list(getpath(tree))
            if len(positions) != len(set(positions)):
                continue

    benchmark(synthesize_and_enumerate)
