from typing import List

import lift
from lift_algorithms.lift import LiftAction
from simulation_handler import User


class LookAlgorithm(lift.BaseLiftAlgorithm):
    def calculate(self, lift_occupants: List[User], floors: List[List[User]], current_time: int, current_floor: int) -> LiftAction:
            pass