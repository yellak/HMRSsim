import esper
import math
import logging
from simulator.typehints.dict_types import SystemArgs

from simpy import FilterStore

from simulator.components.WayPointGoal import WayPointGoal
from simulator.components.Position import Position
from simulator.components.Velocity import Velocity
from simulator.components.Rotatable import Rotatable
from simulator.components.LinearVelocityControl import LinearVelocityControl 
from simulator.components.AngularVelocityControl import AngularVelocityControl 
from simulator.systems.controllers.PID import PID
from simulator.typehints.component_types import EVENT, EndOfMovementPayload, EndOfMovementTag, Point 
from simulator.utils.geometry import get_angle

class DifferentialBaseKinematicProcessor(esper.Processor):
    def __init__(self):
        super().__init__()  
        self.controller = PID()
        self.logger = logging.getLogger(__name__)

    def process(self, kwargs: SystemArgs):
        event_store: FilterStore = kwargs.get('EVENT_STORE', None)
        env = kwargs.get('ENV', None)
        dt: float = kwargs.get('DELTA_TIME', None)
        for ent, (pos, vel, rot, wp_goal, lv_ctrl, av_ctrl) in self.world.get_components(Position, Velocity, Rotatable, WayPointGoal, LinearVelocityControl, AngularVelocityControl):

            point = wp_goal.point
            pos_center = pos.center
            pos_angle = pos.angle
            # The negative signal is because the vertical coordinate (y axe) is inverse
            wp_goal_angle = - get_angle(pos_center, point)
            self.logger.info(f'dt: {dt}')

            if int(pos_center[0] * 100) == int(point[0] * 100) and int(pos_center[1] * 100) == int(point[1] * 100) and int(pos_angle * 100) == int(wp_goal_angle * 100):
                vel.x = 0
                vel.y = 0
                vel.alpha = 0
                pos.changed = False
                end_of_movement = EVENT(EndOfMovementTag, EndOfMovementPayload(ent, str(env.now), target=wp_goal.point, orientation=wp_goal.angle))
                event_store.put(end_of_movement )
                self.world.remove_component(ent, WayPointGoal)
                return
            else:
                v = self.controller.get_output(lv_ctrl, pos_center, point, dt)
                self.logger.info(f'linear velocity: {v}')
                w = self.controller.get_output(av_ctrl, pos_angle, wp_goal_angle, dt)
                self.logger.info(f'angular velocity: {w}')

                vel.x = v * math.cos(pos_angle)

                # The negative signal in vel y and omega, is because the vertical coordinate (y axe) is inverse
                vel.y = - v * math.sin(pos_angle)
                vel.alpha = - w
                self.logger.info(f'velocity: x={vel.x}, y={vel.y}, omega={vel.alpha}')
