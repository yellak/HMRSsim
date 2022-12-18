from simulator.typehints.component_types import Component

class MovableBase(Component):
    """
    MovableBase component store information about motion capabilities of the Entity
    """
    def __init__(self, max_speed=5.0, acceleration=0.5) -> None:
        self.max_speed = max_speed
        self.speed = 0
        self.angular_speed = 5 # graus
        self.initial_speed = 0
        self.acceleration = acceleration 
    
    def __str__(self) -> str:
        return f"MovableBase[max_speed: {self.max_speed}, acceleration: {self.acceleration}, angular_speed: {self.acceleration}]"