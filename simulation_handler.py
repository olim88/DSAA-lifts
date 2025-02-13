import logging
import os
from typing import List, Tuple
import json
import random

from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action
from user import User


def save_simulation(values: List[User], total_floors: int, lift_capacity: int):
    """Saves to the simulation file"""
    # create dictionary to save
    output = {"floors": total_floors, "lift capacity": lift_capacity}
    for value in values:
        output[value.id] = value.get_simulation_data()
    # write to file

    with open(f"simulations/simulation_{len(os.listdir("simulations"))}.json", "w") as f:
        f.write(json.dumps(output, indent=4))


def open_simulation(simulation_id: int) -> Tuple[List[User], int, int]:  # todo handle errors in formating
    """loads the simulation json into a list of users. And the number of floors the simulation has"""
    users = []
    floors = 0
    lift_capacity = 0
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        json_data = json.load(f)
    for key in json_data:
        if key == "floors":
            floors = json_data[key]
            continue
        elif key == "lift capacity":
            lift_capacity = json_data[key]
            continue
        if key.isdigit():
            users.append(User(key, json_data[key][0], json_data[key][1], json_data[key][2]))

    return users, floors, lift_capacity


def save_output(values: List[User], simulation_id: int, algorithm: BaseLiftAlgorithm):
    # load existing file data
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        json_data = json.load(f)
    # create dictionary to save and add to simulation info
    output = {}
    for value in values:
        output[value.id] = value.get_output_data()
    if "algorithm output" not in json_data:
        json_data["algorithm output"] = {}
    json_data["algorithm output"][algorithm.name] = output
    # write all data
    with open(f"simulations/simulation_{simulation_id}.json", "w") as f:
        f.write(json.dumps(json_data, indent=4))


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


def create_simulation_from_inputs():
    floors = int(input("Enter the number of floors: "))
    user_count = int(input("Enter the number of users: "))
    max_start_time = int(input("Enter the maximum start time: "))
    list_capacity = int(input("Enter the capacity of the simulation: "))
    simulation = create_simulation(floors, user_count, max_start_time)
    save_simulation(simulation, floors, list_capacity)
    print("Simulation saved")


def run_simulation(algorithm: BaseLiftAlgorithm, simulation_id: int) -> List[User]:
    # load the constants
    with open("data/constants.json", "r") as f:
        constants = json.load(f)
    # set up values
    (future_users, total_floors, capacity) = open_simulation(simulation_id)
    algorithm.set_capacity(capacity)
    total_users = len(future_users)
    finished_users: List[User] = []
    current_time = 0
    current_floor = constants["start floor"]
    lift_occupants = []
    floors = [[] for floor in range(total_floors)]
    last_action: LiftAction = LiftAction(Action.wait)

    # run lift loop until simulation finished
    while True:
        # check to see if the lift has finished
        if len(finished_users) == total_users:
            break
        # see if any new lift users have arrived since the last action
        for user in future_users:
            if user.start_time <= current_time:
                floors[user.start_floor].append(user)
                future_users.remove(user)

        # send state to lift algorithm
        completed_action: LiftAction = algorithm.calculate(lift_occupants, floors, current_time, current_floor)

        # apply changes from action
        if completed_action.action == Action.wait:
            current_time += 1
        elif completed_action.action == Action.move_up:
            current_floor += 1
            current_time += constants["time between floors"]
            logging.info(f"Going up to floor: {current_floor}")
        elif completed_action.action == Action.move_down:
            current_floor -= 1
            current_time += constants["time between floors"]
            logging.info(f"Going down to floor: {current_floor}")
        elif completed_action.action == Action.open_doors:
            # edit user timings
            for user in completed_action.add:
                user.set_user_start_traveling(current_time)
            for user in completed_action.remove:
                user.set_user_end_traveling(current_time)
            # remove from queue
            floors[current_floor] = [user for user in floors[current_floor] if user not in completed_action.add]
            # change lift occupants
            lift_occupants.extend(completed_action.add)
            lift_occupants = [user for user in lift_occupants if user not in completed_action.remove]
            # add to output
            finished_users.extend(completed_action.remove)
            # calculate time taken
            people_change = len(completed_action.add) + len(
                completed_action.remove)
            current_time += (constants["first pickup time"] if last_action.action != Action.open_doors else 0) + \
                            constants["extra pickup time"] * people_change
            logging.info(f"took on: {len(completed_action.add)}. dropped off: {len(completed_action.remove)}.")
            logging.info(f"there are now {len(lift_occupants)} users in the lift")
        # update last actin
        last_action = completed_action

        logging.info(f"current time: {current_time}. users left: {total_users - len(finished_users)}")

    # return finished users
    return finished_users
