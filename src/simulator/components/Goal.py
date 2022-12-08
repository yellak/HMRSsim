import math
import simulator.utils.helpers as helpers
from simulator.typehints.component_types import Component, Point


class Goal(Component):
    """Goal components hold the target position of an Entity in the esper World.
    """
    def __init__(self, point: Point, angle: float = 0.0, arrived: bool = False):
        self.point = point
        self.angle = angle
        self.arrived = arrived

    def __str__(self):
        return "Goal[({},{}) {}]".format(self.point[0], self.point[1], self.angle)