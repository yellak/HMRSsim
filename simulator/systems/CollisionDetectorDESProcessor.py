from components.Position import Position
from typehints.dict_types import SystemArgs
from components.Collision import Collision

def process(kwargs: SystemArgs):
    event_store = kwargs.get('EVENT_STORE', None)
    world = kwargs.get('WORLD', None)
    if event_store is None:
        raise Exception("Can't find eventStore")
    while True:
        event = yield event_store.get(lambda ev: ev.type == 'stopEvent')
        entity, other_entity = event.payload
        position = world.component_for_entity(entity, Position)

        if world.has_component(entity, Collision):
            collision = world.component_for_entity(entity, Collision)
            collision.add_collision(other_entity, kwargs.get('ENV').now, Position(position.x, position.y))
        else:
            collision = Collision(other_entity, kwargs.get('ENV').now, Position(position.x, position.y))
            world.add_component(entity, collision)
        