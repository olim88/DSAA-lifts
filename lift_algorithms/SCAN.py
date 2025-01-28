from typing import List

from lift_algorithms.lift import LiftAction, Action, BaseLiftAlgorithm, get_can_drop_off
from simulation_handler import User


class ScanAlgorithm(BaseLiftAlgorithm):
    direction: bool  # true == up

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.direction = True

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
            if user.end_floor > current_floor and self.direction or current_floor == len(floors) - 1:
                pick_up.append(user)
            # if lift is going down and there is a user that also wants to go down take them or the lift is about to go up
            elif user.end_floor < current_floor and not self.direction or current_floor == 0:
                pick_up.append(user)

        # based on if lift can do somthing at the floor decide what to do next
        if len(pick_up) > 0 or len(drop_off) > 0:  # todo do nothing if there is nobody waiting
            return LiftAction(Action.open_doors, pick_up, drop_off)
        elif self.direction:
            # switch directions if at the top
            if current_floor == len(floors) - 1:
                self.direction = False
                return LiftAction(Action.move_down)
            return LiftAction(Action.move_up)
        else:
            # switch directions if at the bottom
            if current_floor == 0:
                self.direction = True
                return LiftAction(Action.move_up)
            return LiftAction(Action.move_down)
