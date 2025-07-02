from __future__ import annotations

from dataclasses import dataclass

from cosy import DSL, Constructor, CoSy, Literal, Taxonomy, Type, Var


@dataclass(kw_only=True, frozen=True)
class Structure:
    name: str
    mass: float
    length: float
    dof: int
    centre_of_mass: float

    def new_name(self, *names: str) -> str:
        return f"{self.name}({" ".join(names)})"

    def new_mass(self, *masses: float) -> float:
        return self.mass + sum(masses)

    def new_length(self, *lengths: float) -> float:
        return self.length + sum(lengths)

    def new_centre_of_mass(self, *centres_with_mass: tuple[float, float]) -> float:
        return (
            self.centre_of_mass * self.mass + sum([(self.length + centre) * mass for centre, mass in centres_with_mass])
        ) / (self.mass + sum([mass for _, mass in centres_with_mass]))

    def torque_requirement(self) -> float:
        return self.centre_of_mass * self.mass * 0.0981


@dataclass(kw_only=True, frozen=True)
class Motor(Structure):
    dof: int = 1

    def __call__(self, _previous_dof, dof, connection: Structure):
        name = self.new_name(connection.name)
        mass = self.new_mass(connection.mass)
        centre_of_mass = self.new_centre_of_mass((connection.centre_of_mass, connection.mass))
        length = self.new_length(connection.length)
        return Motor(name=name, mass=mass, length=length, dof=dof, centre_of_mass=centre_of_mass)


@dataclass(kw_only=True, frozen=True)
class Branching(Structure):
    dof: int = 0

    def __call__(
        self, _previous_left_dof, _previous_right_dof, dof, left_connection: Structure, right_connection: Structure
    ):
        name = self.new_name(left_connection.name, right_connection.name)
        mass = self.new_mass(left_connection.mass, right_connection.mass)
        centre_of_mass = self.new_centre_of_mass(
            (left_connection.centre_of_mass, left_connection.mass),
            (right_connection.centre_of_mass, right_connection.mass),
        )
        length = self.new_length(left_connection.length, right_connection.length)
        return Branching(name=name, mass=mass, length=length, dof=dof, centre_of_mass=centre_of_mass)


@dataclass(kw_only=True, frozen=True)
class Extending(Structure):
    dof: int = 0

    def __call__(self, dof, connection: Structure):
        name = self.new_name(connection.name)
        mass = self.new_mass(connection.mass)
        centre_of_mass = self.new_centre_of_mass((connection.centre_of_mass, connection.mass))
        length = self.new_length(connection.length)
        return Extending(name=name, mass=mass, length=length, dof=dof, centre_of_mass=centre_of_mass)


def main():
    """

    :return:
    """

    strong_motor_torque = 3.0
    weak_motor_torque = 1.0

    component_specifications = {
        Motor(name="Strong Motor", mass=1.0, length=5.0, centre_of_mass=2.5): DSL()
        .parameter("previous_dof", "degrees_of_freedom")
        .parameter("dof", "degrees_of_freedom", lambda vs: [vs["previous_dof"] + 1])
        .argument(
            "connection",
            Constructor("InertStructure") & Constructor("kinematic_property", Var("previous_dof")),
        )
        .constraint(lambda vs: vs["connection"].interpret().torque_requirement() < strong_motor_torque)
        .suffix(Constructor("PoweredStructure") & Constructor("kinematic_property", Var("dof"))),
        #
        #
        #
        Motor(name="Weak Motor", mass=0.8, length=5.0, centre_of_mass=2.5): DSL()
        .parameter("previous_dof", "degrees_of_freedom")
        .parameter("dof", "degrees_of_freedom", lambda vs: [vs["previous_dof"] + 1])
        .argument(
            "connection",
            Constructor("InertStructure") & Constructor("kinematic_property", Var("previous_dof")),
        )
        .constraint(lambda vs: vs["connection"].interpret().torque_requirement() < weak_motor_torque)
        .suffix(Constructor("PoweredStructure") & Constructor("kinematic_property", Var("dof"))),
        #
        #
        #
        Branching(name="Branching Part", length=5.0, mass=3.0, centre_of_mass=2.5): DSL()
        .parameter("dof", "degrees_of_freedom")
        .parameter("previous_left_dof", "degrees_of_freedom")
        .parameter("previous_right_dof", "degrees_of_freedom", lambda vs: [vs["dof"] - vs["previous_left_dof"]])
        .argument(
            "left_connection",
            Constructor("PoweredStructure") & Constructor("kinematic_property", Var("previous_left_dof")),
        )
        .argument(
            "right_connection",
            Constructor("PoweredStructure") & Constructor("kinematic_property", Var("previous_right_dof")),
        )
        .suffix(Constructor("InertStructure") & Constructor("kinematic_property", Var("dof"))),
        #
        #
        #
        Extending(name="Extending Part", mass=0.5, length=50.0, centre_of_mass=25.0): DSL()
        .parameter("previous_dof", "degrees_of_freedom")
        .argument(
            "connection",
            Constructor("PoweredStructure") & Constructor("kinematic_property", Var("previous_dof")),
        )
        .suffix(Constructor("InertStructure") & Constructor("kinematic_property", Var("previous_dof"))),
        #
        #
        #
        Motor(name="Effector", mass=0.1, length=5.0, centre_of_mass=2.5): DSL().suffix(
            Constructor("PoweredStructure") & Constructor("kinematic_property", Literal(0, "degrees_of_freedom"))
        ),
    }

    targets = {"dof": 2}
    parameter_space = {
        "degrees_of_freedom": list(range(targets.get("dof") + 1)),
    }
    taxonomy: Taxonomy = {"PoweredStructure": {"Structure"}, "InertStructure": {"Structure"}}

    cosy = CoSy(component_specifications, parameter_space, taxonomy=taxonomy)
    query: Type = Constructor("Structure") & ("kinematic_property" @ Literal(targets.get("dof"), "degrees_of_freedom"))
    for solution in cosy.solve(query):
        print(f"{solution.name}: {solution.torque_requirement()} Nm")


if __name__ == "__main__":
    main()
