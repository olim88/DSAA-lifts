from enum import Enum
from typing import List
from simulation_handler import User

class Action(Enum):
    move_up = 1
    move_down = 2
    open_doors = 3


class LiftAction:
    action: Action
    add: List[User]
    remove: List[User]
    def __init__(self, action: Action, add: List[User] = None, remove: List[User] = None):
        self.action = action
        self.add = add
        self.remove = remove

def get_can_drop_off(current_floor: int, lift_occupants: List[User]) -> List[User]:
    """returns list of users that could be dropped of at the current floor"""
    drop_off = []
    for lift_occupant in lift_occupants:
        if lift_occupant.end_floor == current_floor:
            drop_off.append(lift_occupant)
    return drop_off


class BaseLiftAlgorithm:
    capacity: int
    def __init__(self, capacity: int):
        self.capacity = capacity

    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int, current_floor: int) -> LiftAction:
        pass