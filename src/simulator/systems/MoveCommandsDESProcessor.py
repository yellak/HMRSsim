import logging
from simulator.components.WayPointGoal import WayPointGoal
from simulator.components.Position import Position

from simulator.typehints.component_types import EVENT, ERROR, MoveCommandPayload, MoveCommandEventTag
from simulator.typehints.dict_types import SystemArgs

def init(ros_control=None):
    ros_control = ros_control
    def process(kwargs: SystemArgs):
        logger = logging.getLogger(__name__)
        event_store = kwargs.get('EVENT_STORE', None)
        world = kwargs.get('WORLD', None)
        if event_store is None:
            raise Exception("Can't find eventStore")
        while True:
            event = yield event_store.get(lambda ev: ev.type is MoveCommandEventTag)
            payload: MoveCommandPayload = event.payload
            target = tuple(map(lambda p: float(p), payload.target))
            orientation = payload.orientation
            logger.debug(f'Target position: {target} and orientation: {orientation}')
            entity_pos = world.component_for_entity(payload.entity, Position)
            source = entity_pos.center
            logger.info(f"Current position: x={source[0]:.2f}, y={source[1]:.2f}, theta={entity_pos.angle:.2f}")
            if target == source:
                logger.warning("WARN - Already at destination")
                continue

            new_goal = WayPointGoal(target)
            logger.info(f"New move command received: {new_goal}")
            world.add_component(payload.entity, new_goal)
            
    return process