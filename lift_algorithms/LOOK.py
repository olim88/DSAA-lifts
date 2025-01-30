from typing import List

from lift_algorithms.lift import LiftAction, Action, BaseLiftAlgorithm, get_can_drop_off
from user import User


class LookAlgorithm(BaseLiftAlgorithm):

    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int, current_floor: int) -> LiftAction:
            pass