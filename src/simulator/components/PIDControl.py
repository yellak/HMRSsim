from simulator.typehints.component_types import Component, Point
from typing import Union

class PIDControl(Component):
    def __init__(
        self,
        Kp = 1.0, 
        Kd = 1.0, 
        Ki = 1.0,
        output_limits=(None, None),
        diff = lambda a, b: b - a
    ) -> None:
        self.Kp = Kp 
        self.Kd = Kd 
        self.Ki = Ki
        self.output_limits=output_limits
        self.diff=diff
        self.integrator = 0.0

        self.proportional = 0.0
        self.integral = 0.0
        self.derivative = 0.0

        self.last_error = None
        self.last_output = None
