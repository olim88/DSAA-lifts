import logging
import os
from typing import List, Tuple
import json
import random

from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action
from user import User, UserQueue


def save_simulation(values: List[User], total_floors: int, lift_capacity: int):
    """Saves to the simulation file"""
    # create dictionary to save
    output = {"floors": total_floors, "lift capacity": lift_capacity}
    for value in values:
        output[value.id] = value.get_simulation_data()
    # make sure destination folder exists
    if not os.path.exists("simulations"):
        os.makedirs("simulations")
    # write to file
    with open(f"simulations/simulation_{len(os.listdir("simulations"))}.json", "w") as f:
        f.write(json.dumps(output, indent=4))


def open_simulation(simulation_id: int) -> Tuple[UserQueue, int, int]:
    """loads the simulation json into a list of users. And the number of floors the simulation has"""
    users = []
    floors = 0
    lift_capacity = 0
    # make sure that the file is valid
    try:
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
                # check for valid data
                if len(json_data[key]) == 3 and type(json_data[key][0]) is int and type(
                        json_data[key][1]) is int and type(json_data[key][2]) is int:
                    users.append(User(key, json_data[key][0], json_data[key][1], json_data[key][2]))
                else:
                    raise Exception()

        # add users to a queue in order of arrive time
        user_queue: UserQueue = UserQueue()
        user_quick_sort(users, 0, len(users) - 1)
        for user in users:
            user_queue.enqueue(user)

        return user_queue, floors, lift_capacity
    except FileNotFoundError:
        raise Exception("Simulation file not found.")
    except json.decoder.JSONDecodeError:
        raise Exception("Simulation file not valid json.")
    except KeyError:
        raise Exception("Simulation file not valid json.")
    except:
        raise Exception("Invalid entry in simulation file.")


def user_quick_sort(users: List[User], low: int, high: int):
    """
    Sorts a list of users according to their start time from highest to lowest. Using quick sort.
    :param users: list being sorted
    :param low: the lowest value in part of list to look at
    :param high: the highest value in part of list to look at
    """
    if low < high:
        # find partition
        partition: int = user_quick_sort_partition(users, low, high)
        # sort both sides
        user_quick_sort(users, low, partition - 1)
        user_quick_sort(users, partition + 1, high)


def user_quick_sort_partition(users: List[User], low: int, high: int) -> int:
    """
    Finds the pivot point using the first value in the list
    :param users: list being sorted
    :param low: the lowest value in part of list to look at
    :param high: the highest value in part of list to look at
    :return: pivot point
    """
    pivot: User = users[high]
    i: int = low - 1
    for j in range(low, high):
        # sort from high to low
        if users[j].start_time >= pivot.start_time:
            i += 1
            # swap i and j
            users[i], users[j] = users[j], users[i]

    # do final swap
    users[i + 1], users[high] = users[high], users[i + 1]

    return i + 1


def save_output(values: List[User], simulation_id: int, algorithm: BaseLiftAlgorithm):
    """
    Saves simulation output to the simulation file
    :param values: output of the simulation
    :param simulation_id: id of the simulation
    :param algorithm: algorithm to use to get the output
    """
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
    """
    Creates a simulation based on given parameters
    :param total_floors: total number of floors in the simulation
    :param user_count: how many users to simulate
    :param max_start_time: how long it can take for a user to spawn
    :return: list of users for created simulation
    """
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
    """
    Creates and saves a simulation based on user input
    """
    floors = int(input("Enter the number of floors: "))
    user_count = int(input("Enter the number of users: "))
    max_start_time = int(input("Enter the maximum start time: "))
    list_capacity = int(input("Enter the capacity of the simulation: "))
    simulation = create_simulation(floors, user_count, max_start_time)
    save_simulation(simulation, floors, list_capacity)
    print("Simulation saved")


def run_simulation(algorithm: BaseLiftAlgorithm, simulation_id: int) -> List[User]:
    """
    Runs a given simulation using the given algorithm and id
    :param algorithm: algorithm to use to get the output
    :param simulation_id: simulation id to run
    :return: simulated users with times
    """
    # load the constants
    with open("data/constants.json", "r") as f:
        constants = json.load(f)
    # set up values
    (future_users, total_floors, capacity) = open_simulation(simulation_id)
    algorithm.set_capacity(capacity)
    total_users = future_users.get_size()
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
        while not future_users.is_empty() and future_users.peak().start_time <= current_time:
            user = future_users.pop()
            floors[user.start_floor].append(user)

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
