from simulator.utils.geometry import *
from simulator.systems.controllers.Controller import Controller

# Based in https://github.com/zainkhan-afk/Differential-Drive-Robot-Navigation
class PID(Controller):
    def __init__(
        self,
        kp_linear = 0.1, 
        kd_linear = 0.1, 
        ki_linear = 0,
        kp_angular = 0.1,
        kd_angular = 0.1,
        ki_angular = 0,
        max_linear_speed = 5.0,
        max_angular_speed = 5.0
    ) -> None:

        self.kp_linear = kp_linear
        self.kd_linear = kd_linear
        self.ki_linear = ki_linear

        self.kp_angular = kp_angular
        self.kd_angular = kd_angular
        self.ki_angular = ki_angular

        self.prev_error_position = 0
        self.prev_error_angle = 0
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed

    def get_control_inputs(self, curr_orientation: float, targ_orientation: float, curr_position: Point, targ_position: Point):

        error_position = get_distance(curr_position, targ_position)

        error_angle =  get_dif_angle_rad(get_angle(curr_position, targ_position), curr_orientation)

        linear_velocity_control = self.kp_linear * error_position + self.kd_linear * (error_position - self.prev_error_position)
        angular_velocity_control = self.kp_angular * error_angle + self.kd_angular * (error_angle - self.prev_error_angle)

        self.prev_error_angle = error_angle
        self.prev_error_position = error_position

        if linear_velocity_control > self.max_linear_speed:
            linear_velocity_control = self.max_linear_speed

        if angular_velocity_control > self.max_angular_speed:
            angular_velocity_control = self.max_angular_speed

        return linear_velocity_control, angular_velocity_control