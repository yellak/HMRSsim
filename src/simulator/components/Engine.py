from simulator.typehints.component_types import Component

class Engine(Component):
    """
    Engine component store information about motion capabilities of the Entity
    """
    def __init__(self, max_speed=10.0, acceleration=1.0) -> None:
        self.max_speed = max_speed
        self.initial_speed = 0
        self.acceleration = acceleration 
    
    def __str__(self) -> str:
        return f"Max speed: {self.max_speed} Acceleration: {self.acceleration}"