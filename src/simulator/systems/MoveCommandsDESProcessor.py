import logging
from simulator.components.Path import Path
from simulator.components.Map import Map
from simulator.components.Position import Position

from simulator.typehints.component_types import EVENT, ERROR, GotoPosPayload, GotoPosEventTag
from simulator.typehints.dict_types import SystemArgs
from simulator.utils.Navigation import add_nodes_from_points

def init(ros_control=None):
    ros_control = ros_control
    def process(kwargs: SystemArgs):
        logger = logging.getLogger(__name__)
        event_store = kwargs.get('EVENT_STORE', None)
        world = kwargs.get('WORLD', None)
        world_map = world.component_for_entity(1, Map)
        if event_store is None:
            raise Exception("Can't find eventStore")
        while True:
            # Gets next goto event
            event = yield event_store.get(lambda ev: ev.type is GotoPosEventTag)
            # logger.debug(f'Event received {event}')
            payload: GotoPosPayload = event.payload
            target = tuple(map(lambda p: float(p), payload.target))
            # Position of entity
            entity_pos = world.component_for_entity(payload.entity, Position)
            source = entity_pos.center
            if target == source:
                logger.warning("WARN - Already at destination")
                continue
            reversed_path = []
            reversed_path.append(target)
            new_path = Path(reversed(reversed_path))
            # Expand map with the points found
            # logger.debug(f'Update map with path {new_path}')
            add_nodes_from_points(world_map, new_path.points)
            logger.debug(
                f'Add Path component to entity {payload.entity} - {new_path}')
            world.add_component(payload.entity, new_path)
            
    return process