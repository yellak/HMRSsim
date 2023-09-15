from simulator.components.PIDControl import PIDControl
from simulator.utils.geometry import get_dif_angle_rad

class AngularVelocityControl(PIDControl):
    def __init__(self, Kp=0.5, Kd=0.0, Ki=0.0, output_limits=...) -> None:
        super().__init__(Kp, Kd, Ki, output_limits, get_dif_angle_rad)