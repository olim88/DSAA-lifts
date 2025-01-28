from typing import List
import json
import random


class User:
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
        return [self.start_floor, self.start_traveling_time, self.finish_time]

    def set_user_start_traveling(self, current_time: int):
        self.start_traveling_time = current_time

    def set_user_end_traveling(self, current_time: int):
        self.finish_time = current_time


def save_simulation(values: List[User]):
    """Saves to the simulation file"""
    # create dictionary to save
    output = {}
    for value in values:
        output[value.id] = value.get_simulation_data()
    # write to file
    with open("data/simulation.json", "w") as f:
        f.write(json.dumps(output, indent=4))


def open_simulation() -> List[User]:
    """loads the simulation json into a list of users"""
    users = []
    with open("data/simulation.json", "r") as f:
        json_data = json.load(f)
    for key in json_data:
        users.append(User(key, json_data[key][0],json_data[key][1], json_data[key][2]))

    return users

def save_output(values: List[User]):
    # create dictionary to save
    output = {}
    for value in values:
        output[value.id] = value.get_output_data()
    # write to file
    with open("data/output.json", "w") as f:
        f.write(json.dumps(output, indent=4))


def create_simulation(total_floors: int, user_count: int, max_start_time: int) -> List[User]:
    values = []
    for user_id in range(user_count):

        start_floor = random.randint(0, total_floors - 1)
        end_floor = random.randint(0, total_floors - 1)
        while start_floor == end_floor:
            end_floor = random.randint(0, total_floors - 1)
        start_time = random.randint(0, max_start_time)

        values.append(User(user_id, start_floor, end_floor, start_time))
    return values

if __name__ == "__main__":
    floors = int(input("Enter the number of floors: "))
    user_count = int(input("Enter the number of users: "))
    max_start_time = int(input("Enter the maximum start time: "))
    simulation = create_simulation(floors, user_count, max_start_time)
    save_simulation(simulation)
    print("Simulation saved")