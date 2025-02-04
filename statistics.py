import json
from typing import Tuple, List

import matplotlib.pyplot as plt


def plot_times(data, algorithm: str):
    plt.boxplot(data, tick_labels=["Waiting for lift", "In lift", "Total"])

    # Add labels and title
    plt.title(f"Waiting times ({algorithm})")
    plt.ylabel('Time')

    # show
    plt.show()


def plot_compared_times(index: int, name: str, input_data):
    data = []
    names = []
    for key in input_data:
        data.append(input_data[key][index])
        names.append(key)
    plt.boxplot(data, tick_labels=names)
    # Add labels and title
    plt.title(name)
    plt.ylabel('Time')

    # show
    plt.show()


def get_statistics_of_algorithm(simulation_id: int, algorithm: str) -> Tuple[List[int], List[int], List[int]]:
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    # get data for chosen algorithm
    if algorithm not in raw_data["algorithm output"]:
        raise Exception(f"Algorithm {algorithm} not found.")
    data = raw_data["algorithm output"][algorithm]
    # extract statistics from the data
    total_time_waiting_for_lift = 0
    waiting_times = []
    total_time_in_lift = 0
    inlift_times = []

    for key in data:
        total_time_waiting_for_lift += data[key][1] - data[key][0]
        total_time_in_lift += data[key][2] - data[key][1]
        waiting_times.append(data[key][1] - data[key][0])
        inlift_times.append(data[key][2] - data[key][1])

    total_times = [sum(time) for time in zip(waiting_times, inlift_times)]

    return waiting_times, inlift_times, total_times

def get_combined_statistics(simulation_ids: List[int], algorithm: str) -> Tuple[List[int], List[int], List[int]]:
    waiting_times = []
    inlift_times = []
    total_times = []
    for sim_id in simulation_ids:
        sim_waiting_times, sim_inlift_times, sim_total_times =  get_statistics_of_algorithm(sim_id, algorithm)
        waiting_times.extend(sim_waiting_times)
        inlift_times.extend(sim_inlift_times)
        total_times.extend(sim_total_times)


    return waiting_times, inlift_times, total_times

def show_statistics_of_algorithm(simulation_id: int, algorithm: str):
    waiting_times, inlift_times, total_times = get_statistics_of_algorithm(simulation_id, algorithm)
    show_algorithm_statistics(waiting_times, inlift_times, total_times, algorithm)

def show_combined_statistics_of_algorithm(simulation_ids: List[int], algorithm: str):
    waiting_times, inlift_times, total_times = get_combined_statistics(simulation_ids, algorithm)
    show_algorithm_statistics(waiting_times, inlift_times, total_times, algorithm)

def show_algorithm_statistics(waiting_times: List[int], inlift_times: List[int], total_times: List[int], algorithm: str):
    total_users = len(waiting_times)
    print(f"Algorithm: {algorithm}:")
    print(
        f"\tThe total time waiting for lift is {sum(waiting_times)}. With an average of {sum(waiting_times) / total_users}")
    print(f"\tThe total time in lift is {sum(inlift_times)}. With an average of {sum(inlift_times) / total_users}")
    print(
        f"\tpThe total time spent by users is {sum(waiting_times) + sum(inlift_times)}. With an average of {sum(waiting_times) + sum(inlift_times) / total_users}")

    # show plots
    plot_times([waiting_times, inlift_times, total_times], algorithm)

def show_compare_statistics(simulation_id: int):
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    timing_data = {}
    for key in raw_data["algorithm output"]:
        timing_data[key] = get_statistics_of_algorithm(simulation_id, key)

    # waiting for lift
    plot_compared_times(0, "Waiting for lift comparison", timing_data)
    plot_compared_times(1, "Time in lift comparison", timing_data)
    plot_compared_times(2, "Total time comparison", timing_data)
