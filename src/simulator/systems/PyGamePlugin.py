import pygame
import json
import math
import esper
from simulator.typehints.dict_types import SystemArgs

from simpy import Environment

from simulator.components.WayPointGoal import WayPointGoal
from simulator.components.LinearVelocityControl import LinearVelocityControl 
from simulator.components.AngularVelocityControl import AngularVelocityControl 
from simulator.components.Skeleton import Skeleton
from simulator.components.Position import Position

# class PyGameDebugProcessor(esper.Processor):

    # def __init__(self):
    #     super().__init__()  

    # def process(self, kwargs: SystemArgs):
def init(scan_interval: float):

    def process(kwargs: SystemArgs):
        event_store = kwargs.get('EVENT_STORE', None)
        draw2ent = kwargs.get('DRAW2ENT', None)
        objects = kwargs.get('OBJECTS', None)
        world: esper.World = kwargs.get('WORLD', None)
        env: Environment = kwargs.get('ENV', None)
        if event_store is None:
            raise Exception("Can't find eventStore")
        elif env is None:
            raise Exception("Can't find env")

        # Puts information about the simulation as the first message in the queue
        # window name, width and height
        simulation_skeleton = world.component_for_entity(1, Skeleton)
        size = json.loads(simulation_skeleton.style)

        get_components = world.get_components

        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        BLUE = (50, 50, 255)
        YELLOW = (255, 255, 0)

        sleep = env.timeout

        pygame.init()

        size = (size["width"], size["height"])
        screen = pygame.display.set_mode(size)

        pygame.display.set_caption("HMRSim")
        # clock = pygame.time.Clock()

        image = pygame.image.load('/home/danilo/git/pid_test/robot2.png')
        robot = pygame.transform.scale(image, (50, 50))

        # while running:
        while True:

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         running = False

            screen.fill(BLACK)


            # for ent, (skeleton, position, wp_goal, lv_ctrl, av_ctrl) in get_components(Skeleton, Position, WayPointGoal, LinearVelocityControl, AngularVelocityControl):
            for ent, (skeleton, position, lv_ctrl, av_ctrl) in get_components(Skeleton, Position, LinearVelocityControl, AngularVelocityControl):

                rotated = pygame.transform.rotate(robot, math.degrees(position.angle))
                rect = rotated.get_rect(center=(position.x, position.y))

                # Draw
                # pygame.draw.circle(screen, YELLOW, (wp_goal.point[0], wp_goal.point[1]), 10, 1)
                pygame.draw.circle(screen, YELLOW, (370, 210), 10, 1)
                screen.blit(rotated, rect)

                pygame.display.update()

            # clock.tick(int(1 / scan_interval)) 
            # clock.tick(60) 
            yield sleep(scan_interval)

    def clean():
        pygame.quit()

    return process, clean
