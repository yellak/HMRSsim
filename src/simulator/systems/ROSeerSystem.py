from simulator.typehints.ros_types import RosTopicServer
from simpy import Environment
from esper import World

from std_msgs.msg import String

import logging
import json
import time
import math

from simulator.typehints.dict_types import SystemArgs
from simulator.components.Skeleton import Skeleton
from simulator.components.Position import Position
from simulator.components.Rotatable import Rotatable
from simulator.utils.helpers import update_style_rotation

class ROSeerSystem(RosTopicServer):
    """
    """

    def __init__(self, kwargs: SystemArgs, scan_interval):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.msg_idx = 0
        self.hasListener = False
        self.last_round = {}
        self.time_last_snapshot = time.time()
        self.scan_interval = scan_interval
        self.event_store = kwargs.get('EVENT_STORE', None)
        self.world: World = kwargs.get('WORLD', None)
        self.env: Environment = kwargs.get('ENV', None)

    def process(self, kwargs: SystemArgs):
        event_store = kwargs.get('EVENT_STORE', None)
        world: World = kwargs.get('WORLD', None)
        env: Environment = kwargs.get('ENV', None)


        self.check_listener()

        if time.time() - self.time_last_snapshot < self.scan_interval:
            return

        if self.event_store is None:
            raise Exception("Can't find eventStore")
        elif env is None:
            raise Exception("Can't find env")

        self.check_listener()

        
        if self.msg_idx == 0:

            # Puts information about the simulation as the first message in the queue
            # window name, width and height
            simulation_skeleton = world.component_for_entity(1, Skeleton)
            size = json.loads(simulation_skeleton.style)
            new_message = {
                "timestamp": -1,
                "window_name": simulation_skeleton.id,
                "dimensions": size
            }

            # Scan simulation situation every scan_interval seconds and report
            self.last_round = {}
        else:
            new_message = {
                "timestamp": round(float(env.now), 3)
            }
            for ent, (skeleton, position) in self.world.get_components(Skeleton, Position):
                if ent == 1:  # Entity 1 is the entire model
                    continue
                elif self.last_round.get(ent, (0, None))[0] != 0 and not position.changed and not skeleton.changed:
                    self.last_round[ent] = (2, skeleton.id)
                    continue

                data = {
                    'value': skeleton.value,
                    'x': position.x,
                    'y': position.y,
                    'width': position.w,
                    'height': position.h,
                    'style': skeleton.style
                }

                if world.has_component(ent, Rotatable):
                    rotatable = world.component_for_entity(ent, Rotatable)
                    rotation = math.degrees(rotatable.rotation)
                    data['style'] = update_style_rotation(data['style'], rotation)

                new_message[skeleton.id] = data
                self.last_round[ent] = (2, skeleton.id)
                position.changed = False
                skeleton.changed = False
            # Check for deleted entities
            deleted = []
            for k, v in self.last_round.items():
                if v[0] == 2:
                    self.last_round[k] = (1, v[1])
                elif v[0] == 1:
                    deleted.append(v[1])
                    self.last_round[k] = (0, v[1])
            if len(deleted) > 0:
                new_message['deleted'] = deleted

        self.send_simulation_snapshot(new_message)
        self.time_last_snapshot = time.time()
        self.msg_idx += 1

    def check_listener(self):
        # If new listener reset msg index
        if self.subscription_count > 1 and self.hasListener == False:
            self.msg_idx = 0
            self.hasListener = True
        elif self.subscription_count <= 1 and self.hasListener == True:
            self.hasListener = False

    def send_simulation_snapshot(self, snapshot):
        msg = String()

        # Formating the message that send construct scenario information
        if self.msg_idx == 0:
            data = {}
            data['details'] = snapshot
            msg.data = json.dumps(data)

        elif self.msg_idx == 1:
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