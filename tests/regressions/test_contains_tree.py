# regression test for contains_tree
import pytest

from cosy.dsl import DSL
from cosy.synthesizer import Synthesizer
from cosy.tree import Tree
from cosy.types import Literal, Var


def leaf() -> str:
    return "."


def branch(depth: int, _new_depth: int, left: str, right: str) -> str:
    return f"(B {depth} {left} {right})"


@pytest.fixture
def component_specifications():
    return {
        # recursive unproductive specification
        leaf: DSL().suffix(Literal(0, "int")),
        branch: DSL()
        .parameter("depth", "int")
        .parameter("new_depth", "int", lambda vs: [vs["depth"] - 1])
        .argument("left", Var("new_depth"))
        .argument("right", Var("new_depth"))
        .constraint(lambda vs: vs["left"] == vs["right"])
        .suffix(Var("depth")),
    }


@pytest.fixture
def query():
    return Literal(2, "int")


def test_contains_tree(query, component_specifications) -> None:
    parameter_space = {"int": [0, 1, 2, 3]}
    solution_space = Synthesizer(component_specifications, parameter_space).construct_solution_space(query)

    tree_correct = Tree(
        branch,
        [
            Tree(2),
            Tree(1),
            Tree(branch, [Tree(1), Tree(0), Tree(leaf), Tree(leaf)]),
            Tree(branch, [Tree(1), Tree(0), Tree(leaf), Tree(leaf)]),
        ],
    )

    # a literals 0 are wrongly set to 1
    tree_wrong_1 = Tree(
        branch,
        [
            Tree(2),
            Tree(1),
            Tree(branch, [Tree(1), Tree(1), Tree(leaf), Tree(leaf)]),
            Tree(branch, [Tree(1), Tree(1), Tree(leaf), Tree(leaf)]),
        ],
    )

    # a subtree is missing
    tree_wrong_2 = Tree(
        branch,
        [
            Tree(2),
            Tree(1),
            Tree(branch, [Tree(1), Tree(0), Tree(leaf), Tree(leaf)]),
            Tree(leaf),
        ],
    )

    assert solution_space.contains_tree(query, tree_correct)
    assert not solution_space.contains_tree(query, tree_wrong_1)
    assert not solution_space.contains_tree(query, tree_wrong_2)
