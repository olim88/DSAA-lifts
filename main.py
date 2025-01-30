import json
import logging
import os
import uuid
from typing import List
import simulation_handler
import statistics
from lift_algorithms.LOOK import LookAlgorithm
from lift_algorithms.lift import BaseLiftAlgorithm, LiftAction, Action

from lift_algorithms.SCAN import ScanAlgorithm


def get_sim_id() -> str | None:
    ids = [sim.split("_")[1].split(".")[0] for sim in os.listdir("simulations")]
    print("Simulation IDs: {}".format(", ".join(ids)))
    chosen_id = input(f"Choose a simulation id:")
    if chosen_id not in ids:
        print("Invalid ID")
        return None
    return chosen_id


if __name__ == '__main__':
    # enables  logging
    logging.basicConfig(level=logging.ERROR)
    # give users simple cli to control what to do
    while True:
        user_input = input("""
What do you want to do?:
    0 - quit
    1 - create simulation
    2 - run simulation
    3 - view statistics
    4 - toggle logging
""")

        if user_input == '0':
            break
        elif user_input == '1':
            simulation_handler.create_simulation_from_inputs()
        elif user_input == '2':
            # ask the user for id
            chosen_id = get_sim_id()
            if chosen_id is None:
                continue
            # ask for algorithm
            chosen_algorithm = input("Choose a simulation to run (LOOK or SCAN)")

            if chosen_algorithm == "LOOK":
                algorithm: BaseLiftAlgorithm = LookAlgorithm()
            elif chosen_algorithm == "SCAN":
                algorithm: BaseLiftAlgorithm = ScanAlgorithm()
            else:
                print("Invalid algorithm")
                continue
            # run correct algorithm
            simulation_output = simulation_handler.run_simulation(algorithm, int(chosen_id))

            simulation_handler.save_output(simulation_output, int(chosen_id), algorithm)
        elif user_input == '3':
            # ask the user for id
            chosen_id = get_sim_id()
            if chosen_id is None:
                continue
            # get stats on that id
            try:
                statistics.get_statistics(int(chosen_id), "SCAN")
            except Exception as e:
                print (e)
            try:
                statistics.get_statistics(int(chosen_id), "LOOK")
            except Exception as e:
                print(e)
        elif user_input == '4':
            if logging.getLogger().isEnabledFor(logging.INFO):
                logging.getLogger().setLevel(logging.ERROR)
                print("logging disabled")
            else:
                logging.getLogger().setLevel(logging.INFO)
                print("logging enabled")
