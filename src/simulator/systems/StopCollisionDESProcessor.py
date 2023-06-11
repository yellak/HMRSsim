import logging
import esper
import simpy
from simulator.components.Position import Position
from simulator.components.Velocity import Velocity
from simulator.components.WayPointGoal import WayPointGoal
from simulator.components.CollisionHistory import CollisionHistory
from simulator.components.Path import Path
from simulator.typehints.dict_types import SystemArgs

from simulator.typehints.component_types import EVENT
from simulator.systems.PathProcessor import EndOfPathTag, EndOfPathPayload
from simulator.typehints.component_types import EVENT, EndOfMovementPayload, EndOfMovementTag, Point 
StopEventTag = 'stopEvent'
GenericCollisionTag = 'genericCollision'


def process(kwargs: SystemArgs):
    logger = logging.getLogger(__name__)
    event_store = kwargs.get('EVENT_STORE', None)
    world: esper.World = kwargs.get('WORLD', None)
    env: simpy.Environment = kwargs.get('ENV', None)
    if event_store is None:
        raise Exception("Can't find eventStore")

    while True:
        # Gets next collision event
        event = yield event_store.get(lambda ev: ev.type == StopEventTag or ev.type == GenericCollisionTag)
        if event.type == GenericCollisionTag:
            continue
        (ent, otherEnt) = event.payload
        pos = world.component_for_entity(ent, Position)
        other_pos = world.component_for_entity(otherEnt, Position)
        (mx, my) = pos.center
        (ox, oy) = other_pos.center

        if world.has_component(ent, CollisionHistory):
            position = world.component_for_entity(ent, Position)
            collision = world.component_for_entity(ent, CollisionHistory)
            collision.add_collision(otherEnt, kwargs.get('ENV').now, Position(position.x, position.y))
            continue


        if world.has_component(ent, WayPointGoal):
            wp_goal = world.component_for_entity(ent, WayPointGoal)
            pos = world.component_for_entity(ent, Position)
            vel = world.component_for_entity(ent, Velocity)
            vel.x = 0
            vel.y = 0
            vel.alpha = 0
            pos.changed = False
            end_of_movement = EVENT(EndOfMovementTag, EndOfMovementPayload(ent, str(env.now), target=wp_goal.point, orientation=wp_goal.angle))
            event_store.put(end_of_movement )
            world.remove_component(ent, WayPointGoal)

        # If following path, remove it
        # This can cause failure of other systems.
        # We need to communicate the control system, instead of doing this.
        if world.has_component(ent, Path):
            path = world.component_for_entity(ent, Path)
            end_of_path = EVENT(EndOfPathTag, EndOfPathPayload(ent, str(env.now), path.points))
            event_store.put(end_of_path)
            world.remove_component(ent, Path)