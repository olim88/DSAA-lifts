import json
import logging
from typing import List
import simulation_handler
from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action

from lift_algorithms.SCAN import ScanAlgorithm



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG) # todo this enables debug logging
    # load the constants
    with open("data/constants.json", "r") as f:  # todo have this as part of a simulation file
        constants = json.load(f)
    # set up values
    future_users: List[simulation_handler.User] = simulation_handler.open_simulation()
    total_users = len(future_users)
    finished_users: List[simulation_handler.User] = []
    current_time = 0
    current_floor = constants["start floor"]
    lift_occupants = []
    floors = [[] for floor in range(constants["floors"])]
    # todo choose which algorithm to use
    algorithm: BaseLiftAlgorithm = ScanAlgorithm(constants["capacity"])

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
            #edit user timings
            for user in completed_action.add:
                user.set_user_start_traveling(current_time)
            for user in completed_action.remove:
                user.set_user_end_traveling(current_time)
            #remove from queue
            floors[current_floor] = [user for user in floors[current_floor] if user not in completed_action.add]
            #change lift occupants
            lift_occupants.extend(completed_action.add)
            lift_occupants = [user for user in lift_occupants if user not in completed_action.remove]
            #add to output
            finished_users.extend(completed_action.remove)
            #calculate time taken
            people_change = len(completed_action.add) + len(completed_action.remove) #todo if sombody comes during this time only add extra person time
            current_time += constants["first pickup time"] + constants["extra pickup time"] * (people_change - 1)
            logging.info(f"took on: {len(completed_action.add)}. dropped off: {len(completed_action.remove)}.")
            logging.info(f"there are now {len(lift_occupants)} users in the lift")

        logging.info(f"current time: {current_time}. users left: {total_users - len(finished_users)}")

    # save the times to output
    simulation_handler.save_output(finished_users)
