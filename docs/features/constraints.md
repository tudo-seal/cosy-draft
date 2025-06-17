# Constraints
There are certain aspects of specifications which are difficult to represent nominally.
Such aspects can be simple relationships between numeric parameters, or complex performance characteristics of solutions.

The most general way to specify such aspects is via the `constraint` method provided by the `DSL`.

In the following example we construct binary sequences matching a given regular expression.

First, we specify binary sequences, which are possibly empty sequences of `0`s and `1`s.

```python
def empty() -> str:
    return ""

def zero(s: str) -> str:
    return s + "0"

def one(s: str) -> str:
    return s + "1"
```
with the following specifications
```python
empty: DSL().suffix(Constructor("str")),

zero: DSL()
    .argument("s", Constructor("str"))
    .suffix(Constructor("str")),

one: DSL()
    .argument("s", Constructor("str"))
    .suffix(Constructor("str")),
```

Then, we specify when such sequences match a given regular expression using a `constraint`.
The component `fin` does not change a given sequence `s`.
However, in its specification `s` matches the regular expression given by the parameter `r`.
This exposes a computed property (corresponding resular expression) as a nominal specification (parameter `r`).

```python
def fin(_b: bool, s: str) -> str:
    return s
```
with the following specification
```python
fin: DSL()
    .parameter("r", "regular_expression")
    .argument("s", Constructor("str"))
    # parameter constraint to ensure that s matches the regular expression r
    .constraint(lambda vs: re.fullmatch(vs["r"], vs["s"].interpret()))
    .suffix(Constructor("matches", Var("r"))),
```
In the body of the constraint, parameters are given as their values and arguments are given as their tree representation, which can be interpreted.
Therefore, the value of the parameter `r` is `vs["r"]`.
The interpreted value of the argument `s` is `vs["s"].interpret()`

Using the above specifications we can construct sequences matching specified regular expressions:
```python
# regular expressions
class RegularExpression(Container):
    def __contains__(self, value: object) -> bool:
        return isinstance(value, str)

parameter_space = {"regular_expression": RegularExpression()}

# CoSy instance with the component specifications and parameter space
cosy = CoSy(component_specifications, parameter_space)

# query for sequences matching the regular expression "01+0"
query: Type = Constructor("matches", Literal("01+0", "regular_expression"))

# solve the query and print the solutions
for solution in cosy.solve(query):
    print(solution)
```
The above results in: `010`, `0110`, `01110`, `011110`, ...

### Remarks

- In the above example we are free to change the particular regular expression in the `query`.

- The specialized `parameter_constraint` method provided by the `DSL` can speed up synthesis, if the constraint only involves parameters (and not argunets).
