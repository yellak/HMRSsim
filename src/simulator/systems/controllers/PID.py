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

    # def __init__(
    #     self,
    #     Kp = 0.1, 
    #     Kd = 0.1, 
    #     Ki = 0,
    #     output_limits=(None, None),
    #     compute_error=__compute_error
    # ) -> None:
    #     self.Kp = Kp, 
    #     self.Kd = Kd, 
    #     self.Ki = Ki,
    #     self.__output_limits=output_limits,
    #     self.__compute_error=compute_error

    #     self.__proportional = 0
    #     self.__integral = 0
    #     self.__derivative = 0

    #     self.__last_error = 0
    #     self.__last_input = 0
    #     self.__last_output = 0

        # self.kp_linear = kp_linear
        # self.kd_linear = kd_linear
        # self.ki_linear = ki_linear

        # self.kp_angular = kp_angular
        # self.kd_angular = kd_angular
        # self.ki_angular = ki_angular

        # self.prev_error_position = 0
        # self.prev_error_angle = 0
        # self.max_linear_speed = max_linear_speed
        # self.max_angular_speed = max_angular_speed

    # def get_control_inputs(self, curr_orientation: float, targ_orientation: float, curr_position: Point, targ_position: Point):

    #     error_position = get_distance(curr_position, targ_position)

    #     error_angle =  get_dif_angle_rad(get_angle(curr_position, targ_position), curr_orientation)

    #     linear_velocity_control = self.kp_linear * error_position + self.kd_linear * (error_position - self.prev_error_position)
    #     angular_velocity_control = self.kp_angular * error_angle + self.kd_angular * (error_angle - self.prev_error_angle)

    #     self.prev_error_angle = error_angle
    #     self.prev_error_position = error_position

    #     if linear_velocity_control > self.max_linear_speed:
    #         linear_velocity_control = self.max_linear_speed

    #     if angular_velocity_control > self.max_angular_speed:
    #         angular_velocity_control = self.max_angular_speed

    #     return linear_velocity_control, angular_velocity_control
