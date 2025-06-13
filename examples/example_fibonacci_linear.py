##Fibonacci Linear##
"""
Overall description of this example goes here.
"""

from cosy import CoSy
from cosy.dsl import DSL
from cosy.types import Constructor, Literal, Var


def fst(_x: int, f: tuple[int, int]) -> int:
    """
    Get the first element of a pair.

    :param x: A pair containing two integers.
    :return: The first element of the pair.
    """
    return f[0]


def fib_zero_one() -> tuple[int, int]:
    """
    The pair of Fibonacci numbers at indices 0 and 1.

    :return: The pair of Fibonacci numbers at indices 0 and 1.
    """
    return (0, 1)


def fib_next(_y: int, _x: int, f: tuple[int, int]) -> tuple[int, int]:
    """
    Calculate the pair Fibonacci numbers at a given indices y and y + 1
    using the pair of Fibonacci numbers at indices x = y - 1 and y.

    :param _y: The indices for which the Fibonacci number is calculated.
    :param _x: The indices decremented by 1.
    :param f: The pair of Fibonacci numbers at indices y - 1 and y.
    :return: The pair of Fibonacci numbers at indices y and y + 1.
    """
    return (f[1], f[0] + f[1])


def main():
    component_specifications = {
        fst: DSL()
        .parameter("x", "int")
        .argument("f", Constructor("fibs") & Constructor("at", Var("x")))
        .suffix(Constructor("fib") & Constructor("at", Var("x"))),
        fib_zero_one: DSL().suffix(Constructor("fibs") & Constructor("at", Literal(0, "int"))),
        fib_next: DSL()
        .parameter("y", "int")
        .parameter("x", "int", lambda vs: [vs["y"] - 1])
        .argument("f", Constructor("fibs") & Constructor("at", Var("x")))
        .suffix(Constructor("fibs") & Constructor("at", Var("y"))),
    }

    # range of relevant indices for Fibonacci numbers
    parameter_space = {"int": frozenset(range(6000))}

    # CoSy instance with the component specifications and parameter space
    cosy = CoSy(component_specifications, parameter_space)

    # query for the Fibonacci number at index 5000
    query = Constructor("fib") & Constructor("at", Literal(5000, "int"))

    # solve the query and print the only solution
    print("5000th Fibonacci number:", next(iter(cosy.solve(query))))


if __name__ == "__main__":
    main()
