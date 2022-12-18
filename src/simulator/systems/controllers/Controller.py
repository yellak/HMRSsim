from abc import ABC, abstractclassmethod
from simulator.typehints.component_types import Point

class Controller(ABC):
    def __init__(self) -> None:
        self.max_linear_speed = 0
        self.max_angular_speed = 0
    @abstractclassmethod
    def get_control_inputs(self, curr_orientation: float, targ_orientation: float, curr_position: Point, targ_position: Point):
        pass
