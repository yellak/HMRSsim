import esper
import logging
import math

from datetime import datetime, timedelta
from simulator.typehints.dict_types import SystemArgs

from simulator.components.Position import Position
from simulator.components.Velocity import Velocity


class MovementProcessor(esper.Processor):
    def __init__(self, minx, maxx, miny, maxy, sector_size=50):
        super().__init__()
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy
        self.sector_size = sector_size
        self.logger = logging.getLogger(__name__)
        self.total = timedelta()
        self.runs = 0
        self.created_tiles = False

    def process(self, kwargs: SystemArgs):
        logger = logging.getLogger(__name__)
        dt: float = kwargs.get('DELTA_TIME', None)

        # The Movement Processor is responsible for managing the tiling of the simulation
        # When it starts (which is after the simulation is loaded) it will initialize the sector
        # Of all entities that have a position
        # This is done just once in the first execution
        if not self.created_tiles:
            for ent, (pos,) in self.world.get_components(Position):
                pos.sector = ((pos.y // self.sector_size) * self.maxx) + (pos.x // self.sector_size)
            self.created_tiles = True

        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            new_x = max(self.minx, pos.x + (vel.x * dt))
            new_y = max(self.miny, pos.y + (vel.y * dt))

            if pos.x != new_x or pos.y != new_y or vel.alpha:
                self.logger.info(f'dt: {dt}')
                pos.changed = True
                self.logger.info(f'current angle: {pos.angle}')
                pos.angle = (pos.angle + (vel.alpha * dt)) % (2 * math.pi)
                self.logger.info(f'new angle: {pos.angle}')
                new_x = min(self.maxx - pos.w, new_x)
                new_y = min(self.maxy - pos.h, new_y)
                self.logger.info(f'current position: x={pos.x}, y={pos.y}')
                self.logger.info(f'new position: x={new_x}, y={new_y}')
                pos.x = new_x
                pos.y = new_y
                pos.center = (pos.x + pos.w // 2, pos.y + pos.h // 2)
                pos.sector = ((pos.y // self.sector_size) * self.maxx) + (pos.x // self.sector_size)
                pos.adjacent_sectors = [
                    (pos.sector + dx + dy)
                    for dx in [-1, -1, -1, 1, 1, 1, 0, 0, 0]
                    for dy in [0, -self.maxx, +self.maxx, 0, -self.maxx, +self.maxx, 0, -self.maxx, +self.maxx]
                ]
            else:
                pos.changed = False

    def add_sector_info(self, pos: Position):
        pos.sector = ((pos.y // self.sector_size) * self.maxx) + (pos.x // self.sector_size)