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
    "Class to hold queue of users"
    users: List[User] = []
    size: int = 0

    def peak(self):
        return self.users[-1]
    def pop(self):
        self.size -= 1
        return self.users.pop()
    def enqueue(self, user: User):
        self.size += 1
        self.users.append(user)
    def is_empty(self):
        return self.size == 0
    def get_size(self):
        return self.size


