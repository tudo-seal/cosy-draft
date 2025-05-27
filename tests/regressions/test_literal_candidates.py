# test for candidate generation for assigning values to literal variables

from collections.abc import Container

from cosy.dsl import DSL
from cosy.synthesizer import Synthesizer
from cosy.types import Constructor, Literal, Omega, Type, Var


def test_candidates() -> None:
    # literal varibles can be assigned computed values
    def c(x: bool, y: bool, z: bool) -> str:
        return f"C {x} {y} {z}"

    component_specifications = {
        c: DSL()
        .parameter("x", "bool")
        .parameter_constraint(lambda vs: vs["x"]) # x is True
        .parameter("y", "bool", lambda _vs: [False]) # y is False
        .parameter("z", "bool", lambda vs: [vs["x"]]) # z is equal to x
        .suffix(
            Constructor("a", Var("x"))
            & Constructor("b", Var("y"))
            & Constructor("c", Var("z"))
        )
    }

    def xyz(x: bool | None, y: bool | None, z: bool | None) -> Type:
        return (
            Constructor("a", Omega() if x is None else Literal(x, "bool"))
            & Constructor("b", Omega() if y is None else Literal(y, "bool"))
            & Constructor("c", Omega() if z is None else Literal(z, "bool"))
        )

    parameter_space={"bool": [True, False]}
    synthesizer = Synthesizer(component_specifications, parameter_space)


    for x in [True, False, None]:
        for y in [True, False, None]:
            for z in [True, False, None]:
                target = xyz(x, y, z)
                grammar = synthesizer.construct_solution_space(target)
                result = {tree.interpret() for tree in grammar.enumerate_trees(target)}
                if (not x) or y or (not z):
                    assert len(result) == 0
                else:
                    assert result == {"C True False True"}

def test_multi_values1() -> None:
    # a literal varible can be assigned multiple computed values
    def c(a: int, b: int) -> str:
        return f"C {a} {b}"

    parameter_space = {"int": [0, 1, 2, 3]}
    component_specifications = {
        c: DSL()
        .parameter("a", "int") # a in [0, 1, 2, 3]
        .parameter("b", "int", lambda vs: [vs["a"] - 1, vs["a"] + 1]) # b in [a-1, a+1]
        .suffix(Constructor("c", Var("a")))
    }

    synthesizer = Synthesizer(component_specifications, parameter_space)
    target = Constructor("c", Literal(0, "int"))

    result = synthesizer.construct_solution_space(target)
    assert [tree.interpret() for tree in result.enumerate_trees(target)] == ["C 0 1"]


def test_multi_values2() -> None:
    # a literal varible can be assigned multiple computed values
    def c(a: int, b: int) -> str:
        return f"C {a} {b}"

    parameter_space = {"int": [0, 1, 2, 3]}
    component_specifications = {
        c: DSL()
        .parameter("a", "int")
        .parameter("b", "int", lambda vs: [vs["a"] - 1, vs["a"] + 1])
        .suffix(Constructor("c", Var("a")))
    }

    synthesizer = Synthesizer(component_specifications, parameter_space)
    target = Constructor("c", Literal(1, "int"))

    result = synthesizer.construct_solution_space(target)
    assert {tree.interpret() for tree in result.enumerate_trees(target)} == {"C 1 2", "C 1 0"}


def test_infinite_values() -> None:
    # the number of values for a literal variable can be infinite
    class Nat(Container):
        # represents the set of (arbitrary large) natural numbers
        def __contains__(self, value: object) -> bool:
            return isinstance(value, int) and value >= 0

    def c(x: int, _y: int, b: str) -> str:
        return f"C {x} ({b})"

    parameter_space = {"nat": Nat()}
    target = "c" @ Literal(3, "nat")

    component_specifications = {
        c: DSL()
        .parameter("a", "nat") # a in [0, 1, 2, ...]
        .parameter("b", "nat", lambda vs: [vs["a"] - 1]) # b in [a-1]
        .suffix(("c" @ Var("b")) ** ("c" @ Var("a"))), # c(b) -> c(a)
        "ZERO": "c" @ Literal(0, "nat"), # c(0)
    }

    synthesizer = Synthesizer(component_specifications, parameter_space)
    grammar = synthesizer.construct_solution_space(target)

    assert [tree.interpret() for tree in grammar.enumerate_trees(target)] == ["C 3 (C 2 (C 1 (ZERO)))"]
