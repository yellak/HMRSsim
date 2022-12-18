from simulator.systems.controllers.Controller import Controller
from simulator.utils.geometry import *

# Based in https://github.com/zainkhan-afk/Differential-Drive-Robot-Navigation
class Mpc(Controller):
    def __init__(self) -> None:
        pass
    def get_control_inputs(self, curr_orientation: float, targ_orientation: float, curr_position: Point, targ_position: Point) -> list:
        pass