import logging
from simulator.utils.geometry import *
from simulator.components.PIDControl import PIDControl
from typing import Union

# Based in https://github.com/zainkhan-afk/Differential-Drive-Robot-Navigation
# and https://github.com/m-lundberg/simple-pid

def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value

class PID():
    """An simple adaptation of the PID controller for the ECS architecture"""
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    
    def get_output(self, ctrl: PIDControl, input_: Union[float, Point], target: Union[float, Point], dt: float) -> float:

        # Compute error terms using component specif diff function
        error = ctrl.diff(input_, target)
        self.logger.info(f'error: {error}')
        d_error = error - (ctrl.last_error if (ctrl.last_error is not None) else error)
        ctrl.integrator = ctrl.integrator + error * dt

        # Compute the proportional term
        ctrl.proportional = ctrl.Kp * error
        self.logger.info(f'proportional term: {ctrl.proportional}')

        # Compute the integral term
        ctrl.integral = ctrl.Ki * ctrl.integrator
        ctrl.integral = _clamp(ctrl.integral, ctrl.output_limits)
        self.logger.info(f'integral term: {ctrl.integral}')

        # Compute the derivative term
        ctrl.derivative = ctrl.Kd * d_error / dt
        self.logger.info(f'derivative term: {ctrl.derivative}')

        output = ctrl.proportional + ctrl.integral + ctrl.derivative
        output = _clamp(output, ctrl.output_limits)
        self.logger.info(f'output: {output}')

        # Keep track of state on ctrl component
        ctrl.last_error = error
        ctrl.last_output = output

        return output
