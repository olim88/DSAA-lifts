from enum import Enum
from typing import List
from user import User


class Action(Enum):
    """
    the 4 options a lift algorithm has
    """
    move_up = 1
    move_down = 2
    open_doors = 3
    wait = 4


class LiftAction:
    """
    Stores data about an action a lift algorithm performance
    """
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
    """Basic parts needed for a lift algorithm to be able to be simulated. When simulating a lift it is assumed that a class inherited from this one"""
    capacity: int
    name: str

    def set_capacity(self, capacity: int):
        """
        Used to set the maximum capacity of the lift algorithm
        :param capacity: capacity of the lift algorithm
        """
        self.capacity = capacity

    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int,
                  current_floor: int) -> LiftAction:
        """
        Main part of the lift algorithm. The lift is given the state of the system and needs to return its next action based on how the algorithm works
        :param lift_occupants:
        :param floors:
        :param current_time:
        :param current_floor:
        :return:
        """
        pass
