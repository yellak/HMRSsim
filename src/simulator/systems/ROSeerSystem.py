from simulator.typehints.ros_types import RosTopicServer
from simpy import Environment
from esper import World

from rclpy.action import CancelResponse, GoalResponse
from rclpy.action.server import ServerGoalHandle
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String

import logging
import json
import time
import math

from simulator.components.Skeleton import Skeleton
from simulator.components.Position import Position
from simulator.components.Rotatable import Rotatable
from simulator.utils.helpers import update_style_rotation

class ROSeerSystem(RosTopicServer):
    """
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.event_store = kwargs.get('event_store', None)
        self.world: World = kwargs.get('WORLD', None)
        self.env: Environment = kwargs.get('ENV', None)
        self.msg_idx = 0

    def process(self):

        if self.event_store is None:
            raise Exception("Can't find eventStore")
        elif self.env is None:
            raise Exception("Can't find env")
        
        if self.msg_idx == 0:

            # Puts information about the simulation as the first message in the queue
            # window name, width and height
            simulation_skeleton = self.world.component_for_entity(1, Skeleton)
            size = json.loads(simulation_skeleton.style)
            new_message = {
                "timestamp": -1,
                "window_name": simulation_skeleton.id,
                "dimensions": size
            }
            # Scan simulation situation every scan_interval seconds and report
            last_round: dict = {}
            # Local ref most used functions
            get_components = self.world.get_components

        else:
            new_message = {
                "timestamp": round(float(self.env.now), 3)
            }
            for ent, (skeleton, position) in get_components(Skeleton, Position):
                if ent == 1:  # Entity 1 is the entire model
                    continue
                elif last_round.get(ent, (0, None))[0] != 0 and not position.changed and not skeleton.changed:
                    last_round[ent] = (2, skeleton.id)
                    continue

                data = {
                    'value': skeleton.value,
                    'x': position.x,
                    'y': position.y,
                    'width': position.w,
                    'height': position.h,
                    'style': skeleton.style
                }

                if self.world.has_component(ent, Rotatable):
                    rotatable = self.world.component_for_entity(ent, Rotatable)
                    rotation = math.degrees(rotatable.rotation)
                    data['style'] = update_style_rotation(data['style'], rotation)

                new_message[skeleton.id] = data
                last_round[ent] = (2, skeleton.id)
                position.changed = False
                skeleton.changed = False
            # Check for deleted entities
            deleted = []
            for k, v in last_round.items():
                if v[0] == 2:
                    last_round[k] = (1, v[1])
                elif v[0] == 1:
                    deleted.append(v[1])
                    last_round[k] = (0, v[1])
            if len(deleted) > 0:
                new_message['deleted'] = deleted

        self.send_simulation_snapshot(new_message)
        self.msg_idx += 1


    def send_simulation_snapshot(self, snapshot):
        msg = String()

        # Formating the message that send construct scenario information
        if self.msg_idx == 1:
            scenario = []
            data = {}

            for _, j in enumerate(snapshot):
                scenario.append({j: snapshot[j]})

            data["scenario"] = scenario
            msg.data = json.dumps(data)

        else:
            msg.data = json.dumps(snapshot)
        
        self.publisher.publish(msg)


    def get_name(self):
        return 'live_report'

    def listener_callback(self, msg):
        pass

    def get_listener_callback(self):
        return self.listener_callback