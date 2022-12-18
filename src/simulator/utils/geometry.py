import numpy as np
from simulator.typehints.component_types import Point
import math

def get_distance(position: Point, goal: Point) -> float:
    """Euclidean distance between two points"""
    return np.sqrt((goal[0] - position[0])**2 + (goal[1] - position[1])**2)

def get_angle(position: Point, goal: Point) -> float:
    """Angle in radian between two points"""
    return np.arctan2(goal[1] - position[1], goal[0] - position[0])

def get_dif_angle_rad(x: float, y: float) -> float:
    """Difference between two angle in radians"""
    arg = math.fmod(y-x, 2*math.pi)
    arg = arg + 2*math.pi if arg < 0 else arg
    arg = arg - 2*math.pi if arg > math.pi else arg
    return -arg

def get_dif_angle_deg(x: float, y: float) -> float:
    """Difference between two angle in degrees"""
    arg = math.fmod(y-x, 360)
    arg = arg + 360 if arg < 0 else arg
    arg = arg - 360 if arg > 180 else arg
    return -arg