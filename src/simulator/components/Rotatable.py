from simulator.typehints.component_types import Component

class Rotatable(Component):
    """
    Rotatable component store information about rotation capabilities of the Entity
    """
    def __init__(self, orientation=0.0, rotation=0.0) -> None:
        # The front of the robot in radians
        self.orientation = orientation
        # The rotation applied to the visual representation of the entity in radians
        self.rotation = rotation
    
    def __str__(self) -> str:
        return f"Rotatable[orientation: {self.orientation}, rotation: {self.rotation}]"