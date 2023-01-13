import sys
print(sys.path)

from simulator.systems.MovementProcessor import MovementProcessor
from simulator.systems.CollisionProcessor import CollisionProcessor
from simulator.systems.PathProcessor import PathProcessor

import simulator.systems.EnergyConsumptionDESProcessor as energySystem
import simulator.systems.ManageObjects as ObjectManager
import simulator.systems.ClawDESProcessor as ClawProcessor
import simulator.systems.ScriptEventsDES as ScriptSystem
import simulator.systems.GotoDESProcessor as NavigationSystem
import simulator.systems.SeerPlugin as Seer
import simulator.systems.StopCollisionDESProcessor as StopCollision

from simulator.components.Script import Script

from simulator.main import Simulator
from simulator.utils.ROS2 import ROS2_conn
import rclpy

# from simulator.utils.Firebase import Firebase_conn

def setup():
    rclpy.init()
    # Create a simulation with config
    simulator = Simulator(sys.argv[1])
    # Some simulator objects
    width, height = simulator.window_dimensions
    # window = simulator.window
    eventStore = simulator.KWARGS['EVENT_STORE']
    exitEvent = simulator.EXIT_EVENT
    env = simulator.ENV

    NAMESPACE = 'hospital'
    # firebase = Firebase_conn(NAMESPACE)
    # firebase.clean_old_simulation()
    ros2 = ROS2_conn()
    # build_report = simulator.build_report
    # ros2.seer_consumer(build_report)
    # firebase.send_build_report(build_report)

    extra_instructions = [
        (NavigationSystem.GotoInstructionId, NavigationSystem.goInstruction),
        (ClawProcessor.GrabInstructionTag, ClawProcessor.grabInstruction),
        (ClawProcessor.DropInstructionTag, ClawProcessor.dropInstrution)
    ]
    ScriptProcessor = ScriptSystem.init(extra_instructions, [ClawProcessor.ClawDoneTag])
    NavigationSystemProcess = NavigationSystem.init()

    # Defines and initializes esper.Processor for the simulation
    normal_processors = [
        MovementProcessor(minx=0, miny=0, maxx=width, maxy=height),
        CollisionProcessor(),
        PathProcessor()
    ]
    # Defines DES processors
    des_processors = [
        Seer.init([ros2.seer_consumer], 0.05, False),
        # Seer.init([firebase.seer_consumer], 0.05, False),
        (ClawProcessor.process,),
        (ObjectManager.process,),
        (StopCollision.process,),
        (energySystem.process,),
        (NavigationSystemProcess,),
        (ScriptProcessor,),
    ]
    # Add processors to the simulation, according to processor type
    for p in normal_processors:
        simulator.add_system(p)
    for p in des_processors:
        simulator.add_des_system(p)


    # Create the error handlers dict
    error_handlers = {
        NavigationSystem.PathErrorTag: NavigationSystem.handle_PathError
    }
    # Adding error handlers to the robot
    robot = simulator.objects[0][0]
    script = simulator.world.component_for_entity(robot, Script)
    script.error_handlers = error_handlers

    return simulator, [script]


if __name__ == "__main__":
    simulator, objects = setup()
    script = objects[0]
    simulator.run()
    print("Robot's script logs")
    print("\n".join(script.logs))
    
