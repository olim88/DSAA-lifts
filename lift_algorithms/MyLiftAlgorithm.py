from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action
from user import User


class MyLiftAlgorithm(BaseLiftAlgorithm):
    def __init__(self):
        self.name = "MYLIFT"
        self.capacity = 0
        self.target_floor = None

    def set_capacity(self, capacity):
        self.capacity = capacity

    def calculate(self, lift_occupants, floors, current_time, current_floor):
        # check if anyone needs to leave, or we can pick people up
        people_leaving = [person for person in lift_occupants if person.end_floor == current_floor]
        can_take_more = len(lift_occupants) < self.capacity

        # get anyone waiting at current floor
        if 0 <= current_floor < len(floors):
            waiting_here = floors[current_floor]
        else:
            waiting_here = []

        if people_leaving or (waiting_here and can_take_more):
            # people go off and then pick up as many as have space for
            people_joining = []
            if waiting_here and can_take_more:
                for person in waiting_here:
                    if len(lift_occupants) + len(people_joining) < self.capacity:
                        people_joining.append(person)
                    else:
                        break
            return LiftAction(Action.open_doors, add=people_joining, remove=people_leaving)

        # if we have no target yet or just arrived there, pick a new target
        if self.target_floor is None or self.target_floor == current_floor:
            floor_with_biggest_wait = self._find_floor_with_biggest_wait(floors, current_time)
            if floor_with_biggest_wait == -1:
                # if no one waiting and the lift is empty then  just wait
                if not lift_occupants:
                    self.target_floor = None
                    return LiftAction(Action.wait)
                else:
                    # else head to where the first passenger wants to go
                    self.target_floor = self._clamp_floor(lift_occupants[0].end_floor, floors)
            else:
                self.target_floor = self._clamp_floor(floor_with_biggest_wait, floors)

        # if  at capacity and not dropping anyone off then drop someone inside the lift
        if len(lift_occupants) == self.capacity:
            if not people_leaving and not (waiting_here and can_take_more):
                self.target_floor = self._clamp_floor(lift_occupants[0].end_floor, floors)

        if self.target_floor == -1:
            self.target_floor = None
            return LiftAction(Action.wait)

        # move towards the target if not already there
        if current_floor == self.target_floor:
            return LiftAction(Action.wait)
        elif self.target_floor < current_floor:
            return LiftAction(Action.move_down)
        else:
            return LiftAction(Action.move_up)

    def _clamp_floor(self, floor_index, floors):
        if floor_index == -1:
            return -1
        if floor_index < 0:
            return 0
        if floor_index >= len(floors):
            return len(floors) - 1
        return floor_index

    def _find_floor_with_biggest_wait(self, floors, time_now):
        best_floor = -1
        max_wait = 0
        for i, waiting_list in enumerate(floors):
            if not waiting_list:
                continue
            total = sum(time_now - p.start_time for p in waiting_list)
            if total > max_wait:
                max_wait = total
                best_floor = i
        return best_floor
