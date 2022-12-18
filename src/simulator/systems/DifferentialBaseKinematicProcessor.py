import esper
import math
import logging
from simulator.typehints.dict_types import SystemArgs
import numpy as np

from simpy import FilterStore

from simulator.components.WayPointGoal import WayPointGoal
from simulator.components.Position import Position
from simulator.components.Velocity import Velocity
from simulator.components.MovableBase import MovableBase
from simulator.systems.controllers.Controller import Controller
from simulator.typehints.component_types import EVENT, EndOfMovementPayload, EndOfMovementTag, Point 

class DifferentialBaseKinematicProcessor(esper.Processor):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller
        self.logger = logging.getLogger(__name__)

    def process(self, kwargs: SystemArgs):
        event_store: FilterStore = kwargs.get('EVENT_STORE', None)
        env = kwargs.get('ENV', None)
        for ent, (pos, wp_goal, mov_base, vel) in self.world.get_components(Position, WayPointGoal, MovableBase, Velocity):

            point = wp_goal.point
            pos_center = pos.center
            pos_angle = pos.angle
            wp_goal_angle = wp_goal.angle

            if int(pos_center[0] * 100) == int(point[0] * 100) and int(pos_center[1] * 100) == int(point[1] * 100) and int(pos_angle * 100) == int(goal_angle * 100):
                vel.x = 0
                vel.y = 0
                vel.alpha = 0
                pos.changed = False
                end_of_movement = EVENT(EndOfMovementTag, EndOfMovementPayload(ent, str(env.now), target=wp_goal.point, orientation=goal.angle))
                event_store.put(end_of_movement )
                self.world.remove_component(ent, WayPointGoal)
                return
            else:
                self.controller.max_angular_speed = mov_base.max_speed 
                self.controller.max_linear_speed = mov_base.angular_speed
                v, w = self.controller.get_control_inputs(np.deg2rad(pos_angle), np.deg2rad(wp_goal_angle), pos_center, point)
                vel.x = v * math.cos(pos_angle)
                vel.y = v * math.sin(pos_angle)
                vel.alpha = np.rad2deg(w)
