from typing import List

from lift_algorithms.SCAN import ScanAlgorithm
from lift_algorithms.lift import LiftAction, Action, BaseLiftAlgorithm, get_can_drop_off
from user import User


class LookAlgorithm(ScanAlgorithm):
    """Enhanced version of SCAN algorithm. Where the lift turns around if there is nobody waiting in the direction it is going"""


    def __init__(self):
        super().__init__()
        self.name = "LOOK"

    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int,
                  current_floor: int) -> LiftAction:
        """works out the next best move the algorithm can make"""

        # run rest of SCAN algorithm
        output: LiftAction = super().calculate(lift_occupants, floors, current_time, current_floor)

        #check to turn around the lift
        if (output.action == Action.move_up or output.action == Action.move_down) and self.should_change_direction(floors, current_floor,lift_occupants):
            self.direction = not self.direction
            if output.action == Action.move_up:
                output.action = Action.move_down
            else:
                output.action = Action.move_up

        return output

    def should_change_direction(self, floors: List[List[User]], current_floor: int, lift_occupants: List[User]) -> bool:
        """adds an extra reason to change the current direction over SCAN algorithm"""
        # see if anybody can be dropped off
        drop_off = get_can_drop_off(current_floor, lift_occupants)
        # see if there is anybody to collect in the direction the lift is going and if not flip direction
        if len(drop_off) == len(lift_occupants):
            if self.direction:
                #makesure that nobody is about to get on and go up
                going_up = all(user.end_floor> user.end_floor for user in floors[current_floor])
                # check if floors above have people waiting
                empty_above = all(len(floors[floor]) == 0 for floor in range(current_floor + 1, len(floors)))
                if going_up and empty_above:
                    return True
            else:
                # makesure that nobody is about to get on and go down
                going_down = all(user.end_floor < user.end_floor for user in floors[current_floor])
                # check if people are waiting below
                empty_above = all(len(floors[floor]) == 0 for floor in range(current_floor, -1, -1))
                if going_down and empty_above:
                    return True


        return super().should_change_direction(floors, current_floor, lift_occupants)