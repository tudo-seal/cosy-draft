##Constraints##
"""
Demonstrates constraints in CoSy.
"""

import re
from collections.abc import Container

from cosy import CoSy
from cosy.dsl import DSL
from cosy.types import Constructor, Literal, Type, Var


def empty() -> str:
    """
    Return an empty string.

    :return: An empty string.
    """
    return ""


def zero(s: str) -> str:
    """
    Append the string "0" to the input string.

    :param s: The input string to which "0" will be appended.
    :return: The input string with "0" appended.
    """
    return s + "0"


def one(s: str) -> str:
    """
    Append the string "1" to the input string.

    :param s: The input string to which "1" will be appended.
    :return: The input string with "1" appended.
    """
    return s + "1"


def fin(_b: bool, s: str) -> str:
    return s


def is_heavy(s: str) -> bool:
    """
    Check if the number of '1's in the string is greater than the number of '0's.

    :param s: A string containing '0's and '1's.
    :return: True if the number of '1's is greater than the number of '0's, False otherwise.
    """
    return s.count("0") < s.count("1")


def main():
    component_specifications = {
        empty: DSL().suffix(Constructor("str")),
        zero: DSL().argument("s", Constructor("str")).suffix(Constructor("str")),
        one: DSL().argument("s", Constructor("str")).suffix(Constructor("str")),
        fin: DSL()
        .parameter("r", "regular_expression")
        .argument("s", Constructor("str"))
        # parameter constraint to ensure that s matches the regular expression r
        .constraint(lambda vs: re.fullmatch(vs["r"], vs["s"].interpret()))
        .suffix(Constructor("matches", Var("r"))),
    }

    # regular expressions
    class RegularExpression(Container):
        def __contains__(self, value: object) -> bool:
            return isinstance(value, str)

    parameter_space = {"regular_expression": RegularExpression()}

    # CoSy instance with the component specifications and parameter space
    cosy = CoSy(component_specifications, parameter_space)

    # query for heavy strings
    query: Type = Constructor("matches", Literal("01+0", "regular_expression"))

    # solve the query and print the solutions
    for solution in cosy.solve(query):
        print(solution)


if __name__ == "__main__":
    main()
