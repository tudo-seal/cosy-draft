"""Synthesizer implementing Finite Combinatory Logic with Predicates.
It constructs a logic program via `constructSolutionSpace` from the following ingredients:
- collection of component specifications
- parameter space
- optional specification taxonomy
- target specification"""

from collections import deque
from collections.abc import (
    Callable,
    Container,
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from dataclasses import dataclass
from functools import reduce
from typing import (
    Any,
    Generic,
    TypeVar,
)

from cosy.combinatorics import maximal_elements, minimal_covers
from cosy.solution_space import (
    Argument,
    ConstantOrigin,
    NonTerminalOrigin,
    RHSRule,
    SolutionSpace,
)
from cosy.subtypes import Subtypes, Taxonomy
from cosy.tree import Tree
from cosy.types import (
    Abstraction,
    Arrow,
    Implication,
    Intersection,
    LiteralParameter,
    Parameter,
    Predicate,
    TermParameter,
    Type,
)

# type of components
C = TypeVar("C", bound=Hashable)

# type of component specifications
Specification = Abstraction | Implication | Type

# type of parameter space
ParameterSpace = Mapping[str, Iterable | Container]


@dataclass(frozen=True)
class MultiArrow:
    # type of shape arg1 -> arg2 -> ... -> argN -> target
    args: tuple[Type, ...]
    target: Type

    def __str__(self) -> str:
        if len(self.args) > 0:
            return f"{[str(a) for a in self.args]} -> {self.target!s}"
        return str(self.target)


@dataclass()
class CombinatorInfo:
    # container for auxiliary information about a combinator
    prefix: list[LiteralParameter | TermParameter | Predicate]
    groups: dict[str, str]
    term_predicates: tuple[Callable[[dict[str, Any]], bool], ...]
    instantiations: deque[dict[str, Any]] | None
    type: list[list[MultiArrow]]


class Synthesizer(Generic[C]):
    def __init__(
        self,
        component_specifications: Mapping[C, Specification],
        parameter_space: ParameterSpace | None = None,
        taxonomy: Taxonomy | None = None,
    ):
        self.literals: ParameterSpace = (
            {} if parameter_space is None else dict(parameter_space.items())
        )
        self.repository: tuple[tuple[C, CombinatorInfo], ...] = tuple(
            (c, Synthesizer._function_types(self.literals, ty))
            for c, ty in component_specifications.items()
        )
        self.subtypes = Subtypes(taxonomy if taxonomy is not None else {})

    @staticmethod
    def _function_types(
        literals: ParameterSpace,
        parameterized_type: Specification,
    ) -> CombinatorInfo:
        """Presents a type as a list of 0-ary, 1-ary, ..., n-ary function types."""

        def unary_function_types(ty: Type) -> Iterable[tuple[Type, Type]]:
            tys: deque[Type] = deque((ty,))
            while tys:
                match tys.pop():
                    case Arrow(src, tgt) if not tgt.is_omega:
                        yield (src, tgt)
                    case Intersection(sigma, tau):
                        tys.extend((sigma, tau))

        prefix: list[LiteralParameter | TermParameter | Predicate] = []
        variables: set[str] = set()
        groups: dict[str, str] = {}
        while not isinstance(parameterized_type, Type):
            if isinstance(parameterized_type, Abstraction):
                param = parameterized_type.parameter
                if param.name in variables:
                    # check if parameter names are unique
                    msg = f"Duplicate name: {param.name}"
                    raise ValueError(msg)
                variables.add(param.name)
                if isinstance(param, LiteralParameter):
                    prefix.append(param)
                    groups[param.name] = param.group
                    # check if group is defined in the parameter space
                    if param.group not in literals:
                        msg = f"Group {param.group} is not defined in the parameter space."
                        raise ValueError(msg)
                elif isinstance(param, TermParameter):
                    prefix.append(param)
                    for free_var in param.group.free_vars:
                        if free_var not in groups:
                            # check if each parameter variable is abstracted
                            msg = f"Parameter {free_var} is not abstracted."
                            raise ValueError(msg)
                parameterized_type = parameterized_type.body
            elif isinstance(parameterized_type, Implication):
                prefix.append(parameterized_type.predicate)
                parameterized_type = parameterized_type.body

        for free_var in parameterized_type.free_vars:
            if free_var not in groups:
                # check if each parameter variable is abstracted
                msg = f"Parameter {free_var} is not abstracted."
                raise ValueError(msg)

        current: list[MultiArrow] = [MultiArrow((), parameterized_type)]

        multiarrows = []
        while len(current) != 0:
            multiarrows.append(current)
            current = [
                MultiArrow((*c.args, new_arg), new_tgt)
                for c in current
                for (new_arg, new_tgt) in unary_function_types(c.target)
            ]

        term_predicates: tuple[Callable[[dict[str, Any]], bool], ...] = tuple(
            p.constraint
            for p in prefix
            if isinstance(p, Predicate) and not p.only_literals
        )
        return CombinatorInfo(prefix, groups, term_predicates, None, multiarrows)

    def _enumerate_substitutions(
        self,
        prefix: list[LiteralParameter | TermParameter | Predicate],
        substitution: dict[str, Any],
    ) -> Iterable[dict[str, Any]]:
        """Enumerate all substitutions for the given parameters fairly.
        Take initial_substitution with inferred literals into account."""

        stack: deque[tuple[dict[str, Any], int, Iterator[Any] | None]] = deque(
            [(substitution, 0, None)]
        )

        while stack:
            substitution, index, generator = stack.pop()
            if index >= len(prefix):
                # no more parameters to process
                yield substitution
                continue
            parameter = prefix[index]
            if isinstance(parameter, LiteralParameter):
                if generator is None:
                    if parameter.name in substitution:
                        value = substitution[parameter.name]
                        if (
                            parameter.values is not None
                            and value not in parameter.values(substitution)
                        ):
                            # the inferred value is not in the set of values
                            continue
                        if value not in self.literals[parameter.group]:
                            # the inferred value is not in the group
                            continue
                        stack.appendleft((substitution, index + 1, None))
                    elif parameter.values is not None:
                        stack.appendleft(
                            (substitution, index, iter(parameter.values(substitution)))
                        )
                    else:
                        concrete_values = self.literals[parameter.group]
                        if not isinstance(concrete_values, Iterable):
                            msg = (
                                f"The value of {parameter.name} could not be inferred."
                            )
                            raise RuntimeError(msg)
                        else:
                            stack.appendleft(
                                (substitution, index, iter(concrete_values))
                            )
                else:
                    try:
                        value = next(generator)
                    except StopIteration:
                        continue
                    if value in self.literals[parameter.group]:
                        stack.appendleft(
                            ({**substitution, parameter.name: value}, index + 1, None)
                        )
                    stack.appendleft((substitution, index, generator))

            elif isinstance(parameter, Predicate) and parameter.only_literals:
                if parameter.constraint(substitution):
                    # the predicate is satisfied
                    stack.appendleft((substitution, index + 1, None))
            else:
                stack.appendleft((substitution, index + 1, None))

    def _subqueries(
        self,
        nary_types: list[MultiArrow],
        paths: Iterable[Type],
        groups: dict[str, str],
        substitution: dict[str, Any],
    ) -> Sequence[list[Type]]:
        # does the target of a multi-arrow contain a given type?
        def target_contains(m: MultiArrow, t: Type) -> bool:
            return self.subtypes.check_subtype(m.target, t, groups, substitution)

        # cover target using targets of multi-arrows in nary_types
        covers = minimal_covers(nary_types, paths, target_contains)
        if len(covers) == 0:
            return []

        # intersect corresponding arguments of multi-arrows in each cover
        def intersect_args(
            args1: Iterable[Type], args2: Iterable[Type]
        ) -> tuple[Type, ...]:
            return tuple(Intersection(a, b) for a, b in zip(args1, args2, strict=False))

        intersected_args: Generator[list[Type]] = (
            list(reduce(intersect_args, (m.args for m in ms))) for ms in covers
        )

        # consider only maximal argument vectors
        def compare_args(args1, args2) -> bool:
            return all(
                map(
                    lambda a, b: self.subtypes.check_subtype(
                        a, b, groups, substitution
                    ),
                    args1,
                    args2,
                )
            )

        return maximal_elements(intersected_args, compare_args)

    def _necessary_substitution(
        self,
        paths: Iterable[Type],
        combinator_type: list[list[MultiArrow]],
        groups: dict[str, str],
    ) -> dict[str, Any] | None:
        """
        Computes a substitution that needs to be part of every substitution S such that
        S(combinator_type) <= paths.

        If no substitution can make this valid, None is returned.
        """

        result: dict[str, Any] = {}

        for path in paths:
            unique_substitution: dict[str, Any] | None = None
            is_unique = True

            for nary_types in combinator_type:
                for ty in nary_types:
                    substitution = self.subtypes.infer_substitution(
                        ty.target, path, groups
                    )
                    if substitution is None:
                        continue
                    if unique_substitution is None:
                        unique_substitution = substitution
                    else:
                        is_unique = False
                        break
                if not is_unique:
                    break

            if unique_substitution is None:
                return None  # no substitution for this path
            if not is_unique:
                continue  # substitution not unique substitution — skip

            # merge consistent substitution
            for k, v in unique_substitution.items():
                if k in result:
                    if result[k] != v:
                        return None  # conflict in necessary substitution
                else:
                    result[k] = v

        return result

    def construct_solution_space_rules(
        self, *targets: Type
    ) -> Generator[tuple[Type, RHSRule]]:
        """Generate logic program rules for the given target types."""

        # current target types
        stack: deque[tuple[Type, tuple[C, CombinatorInfo, Iterator] | None]] = deque(
            (target, None) for target in targets
        )
        seen: set[Type] = set()

        while stack:
            current_target, current_target_info = stack.pop()
            # if the target is omega, then the result is junk
            if current_target.is_omega:
                msg = f"Target type {current_target} is omega."
                raise ValueError(msg)

            # target type was not initialized before
            if current_target not in seen or current_target_info is not None:
                if current_target_info is None:
                    seen.add(current_target)
                    # try each combinator
                    for combinator, combinator_info in self.repository:
                        # Compute necessary substitutions
                        substitution = self._necessary_substitution(
                            current_target.organized,
                            combinator_info.type,
                            combinator_info.groups,
                        )

                        # If there cannot be a suitable substitution, ignore this combinator
                        if substitution is None:
                            continue

                        # Keep necessary substitutions and enumerate the rest
                        selected_instantiations = self._enumerate_substitutions(
                            combinator_info.prefix, substitution
                        )
                        stack.appendleft(
                            (
                                current_target,
                                (
                                    combinator,
                                    combinator_info,
                                    iter(selected_instantiations),
                                ),
                            )
                        )
                else:
                    combinator, combinator_info, selected_instantiations = (
                        current_target_info
                    )
                    instantiation = next(selected_instantiations, None)
                    if instantiation is not None:
                        stack.appendleft((current_target, current_target_info))
                        named_arguments: tuple[Argument, ...] | None = None

                        # and every arity of the combinator type
                        for nary_types in combinator_info.type:
                            for subquery in self._subqueries(
                                nary_types,
                                current_target.organized,
                                combinator_info.groups,
                                instantiation,
                            ):
                                if (
                                    named_arguments is None
                                ):  # do this only once for each instantiation
                                    named_arguments = tuple(
                                        Argument(
                                            param.name,
                                            ConstantOrigin(
                                                combinator_info.groups[param.name]
                                            ),
                                            Tree(instantiation[param.name]),
                                        )
                                        if isinstance(param, LiteralParameter)
                                        else Argument(
                                            param.name,
                                            NonTerminalOrigin(
                                                param.group.subst(
                                                    combinator_info.groups,
                                                    instantiation,
                                                )
                                            ),
                                        )
                                        for param in combinator_info.prefix
                                        if isinstance(param, Parameter)
                                    )
                                    stack.extendleft(
                                        (argument.origin.value, None)
                                        for argument in named_arguments
                                        if isinstance(
                                            argument.origin, NonTerminalOrigin
                                        )
                                    )

                                anonymous_arguments: tuple[Argument, ...] = tuple(
                                    Argument(
                                        None,
                                        NonTerminalOrigin(
                                            ty.subst(
                                                combinator_info.groups, instantiation
                                            )
                                        ),
                                    )
                                    for ty in subquery
                                )
                                yield (
                                    current_target,
                                    RHSRule[Type, Any, Any](
                                        (*named_arguments, *anonymous_arguments),
                                        combinator_info.term_predicates,
                                        combinator,
                                    ),
                                )
                                stack.extendleft(
                                    (q.origin.value, None) for q in anonymous_arguments
                                )

    def construct_solution_space(self, *targets: Type) -> SolutionSpace[Type, C, Any]:
        """Constructs a logic program in the current environment for the given target types."""

        solution_space: SolutionSpace[Type, C, Any] = SolutionSpace()
        for nt, rule in self.construct_solution_space_rules(*targets):
            solution_space.add_rule(nt, rule.terminal, rule.arguments, rule.predicates)

        return solution_space
