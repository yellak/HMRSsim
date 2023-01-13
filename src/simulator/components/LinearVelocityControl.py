from simulator.components.PIDControl import PIDControl
from simulator.utils.geometry import get_distance

class LinearVelocityControl(PIDControl):
    def __init__(self, Kp=1.0, Kd=0.0, Ki=0.0, output_limits=...) -> None:
        super().__init__(Kp, Kd, Ki, output_limits, get_distance)