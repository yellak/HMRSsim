import esper
import math
import logging
from simulator.typehints.dict_types import SystemArgs

from simpy import FilterStore

from simulator.components.Goal import Goal
from simulator.components.Position import Position
from simulator.components.Velocity import Velocity
from simulator.components.Engine import Engine
from simulator.typehints.component_types import EVENT, EndOfMovementPayload, EndOfMovementTag 

class DifferentialBaseKinematicProcessor(esper.Processor):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def process(self, kwargs: SystemArgs):
        event_store: FilterStore = kwargs.get('EVENT_STORE', None)
        env = kwargs.get('ENV', None)
        for ent, (pos, goal, eng, vel) in self.world.get_components(Position, Goal, Engine, Velocity):

            eng.speed += eng.acceleration
            eng.speed = eng.speed if eng.speed < eng.max_speed else eng.max_speed

            point = goal.point
            goal_angle = goal.angle
            pos_center = pos.center
            pos_angle = pos.angle
            if pos_center[0] == point[0] and pos_center[1] == point[1] and pos_angle == goal_angle:
                vel.x = 0
                vel.y = 0
                vel.alpha = 0
                pos.changed = False
                end_of_movement = EVENT(EndOfMovementTag, EndOfMovementPayload(ent, str(env.now), goal=goal.point, orientation=goal.angle))
                event_store.put(end_of_movement )
                self.world.remove_component(ent, Goal)
                return
            else:

                dw = goal_angle - pos_angle
                if dw > 0:
                    vel.alpha = min(eng.angular_speed, dw)
                else:
                    vel.alpha = max(-eng.angular_speed, dw)

                vel_x = eng.speed * math.cos(pos_angle)
                vel_y = -eng.speed * math.sin(pos_angle)

                dx = point[0] - pos_center[0]
                if dx > 0:
                    vel.x = min(vel_x, dx)
                else:
                    vel.x = max(- vel_x, dx)

                dy = point[1] - pos_center[1]
                if dy > 0:
                    vel.y = min(vel_y, dy)
                else:
                    vel.y = max(- vel_y, dy)