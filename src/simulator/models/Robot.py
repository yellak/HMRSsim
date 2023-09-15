from simulator import primitives as primitives
from simulator.components.Velocity import Velocity
from simulator.components.Rotatable import Rotatable
from simulator.components.AngularVelocityControl import AngularVelocityControl
from simulator.components.LinearVelocityControl import LinearVelocityControl
from simulator.components.NavToPoseRosGoal import NavToPoseRosGoal
import math

from typing import Tuple, List
from simulator.typehints.component_types import Component

from simulator.models.Shape import from_object as shape_model_object

MODEL = 'robot'

def from_object(el, line_width=10) -> Tuple[List[Component], dict]:
    options = el.attrib
    components, style = shape_model_object(el, line_width)
    
    if options['type'] == 'robot':
        ros_goal_comp = NavToPoseRosGoal()
        orientation = 0
        rotation = 0
        if 'name' in options:
            ros_goal_comp.name = options["name"]
        # The orientation option indicates the front of the robot in degrees
        if 'orientation' in options:
            orientation = - float(options['orientation'])
        if style.get('rotation', '') != '':
            rotation = float(style['rotation'])
        components.append(ros_goal_comp)
        components.append(Rotatable(orientation=math.radians(orientation), rotation=math.radians(rotation)))
        components.append(Velocity(x=0, y=0))
        components.append(LinearVelocityControl(output_limits=(-10, 10)))
        components.append(AngularVelocityControl(output_limits=(-math.pi/8, math.pi/8)))
    return components, options