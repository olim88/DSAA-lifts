from typing import List


class User:
    """
    Class to hold the user details
    """
    id: int
    start_floor: int
    end_floor: int
    start_time: int
    start_traveling_time: int
    finish_time: int

    def __init__(self, id: int, start_floor: int, end_floor: int, start_time: int):
        self.id = id
        self.start_floor = start_floor
        self.end_floor = end_floor
        self.start_time = start_time

    def get_simulation_data(self) -> List[int]:
        return [self.start_floor, self.end_floor, self.start_time]

    def get_output_data(self) -> List[int]:
        return [self.start_time, self.start_traveling_time, self.finish_time]

    def set_user_start_traveling(self, current_time: int):
        self.start_traveling_time = current_time

    def set_user_end_traveling(self, current_time: int):
        self.finish_time = current_time


class UserQueue:
    users: List[User] = []

    def peak(self):
        return self.users[-1]
    def pop(self):
        return self.users.pop()
    def push(self, user: User):
        self.users.append(user)
    def is_empty(self):
        return len(self.users) == 0
    def get_size(self):
        return len(self.users)


