from typing import List

from lift_algorithms.lift import LiftAction, Action, BaseLiftAlgorithm, get_can_drop_off
from simulation_handler import User


class ScanAlgorithm(BaseLiftAlgorithm):
    """
    Lift algorithm that goes all the way to the top and then to the bottom picking up users going in the correct direction
    """
    direction: bool  # true == up

    def __init__(self):
        self.direction = True
        self.name = "SCAN"

    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int,
                  current_floor: int) -> LiftAction:
        """works out the next best move the algorithm can make"""
        # see if anybody can be dropped off
        drop_off = get_can_drop_off(current_floor, lift_occupants)
        # see if anybody can be picked up
        pick_up = []
        for user in floors[current_floor]:
            # stop trying to pickup if there is no room
            if len(pick_up) + len(lift_occupants) - len(drop_off) >= self.capacity:
                break
            # if lift is going up and there is a user that also wants to take them up
            if user.end_floor > current_floor and self.direction or self.should_change_direction(floors, current_floor,
                                                                                                 lift_occupants):
                pick_up.append(user)
            # if lift is going down and there is a user that also wants to go down take them or the lift is about to go up
            elif user.end_floor < current_floor and not self.direction or self.should_change_direction(floors,
                                                                                                       current_floor,
                                                                                                       lift_occupants):
                pick_up.append(user)

        # based on if lift can do somthing at the floor decide what to do next
        if len(pick_up) > 0 or len(drop_off) > 0:
            return LiftAction(Action.open_doors, pick_up, drop_off)

        # make sure there is a person to move to
        if all(len(floor) == 0 for floor in floors) and len(lift_occupants) == 0:
            return LiftAction(Action.wait, [], [])

        # otherwise move
        if self.should_change_direction(floors, current_floor, lift_occupants):
            self.direction = not self.direction
        if self.direction:
            return LiftAction(Action.move_up)
        else:
            return LiftAction(Action.move_down)

    def should_change_direction(self, floors: List[List[User]], current_floor: int, lift_occupants: List[User]) -> bool:
        if self.direction:
            return current_floor == len(floors) - 1
        else:
            return current_floor == 0
