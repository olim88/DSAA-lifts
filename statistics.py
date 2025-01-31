import json
from typing import Tuple, List

import matplotlib.pyplot as plt




def plot_times(data, algorithm :str):
    plt.boxplot(data, tick_labels=["Waiting for lift", "In lift", "Total"])

    # Add labels and title
    plt.title(f"Waiting times ({algorithm})")
    plt.ylabel('Time')

    #show
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

def get_statistics_of_algorithm(simulation_id: int, algorithm: str)-> Tuple[List[int], List[int], List[int]]:
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    #get data for chosen algorithm
    if algorithm not in raw_data["algorithm output"]:
        raise Exception(f"Algorithm {algorithm} not found.")
    data = raw_data["algorithm output"][algorithm]
    # extract statistics from the data
    total_time_waiting_for_lift = 0
    waiting_times = []
    total_time_in_lift = 0
    inlift_times = []
    total_users = len(data)
    for key in data:
        total_time_waiting_for_lift += data[key][1] - data[key][0]
        total_time_in_lift += data[key][2] - data[key][1]
        waiting_times.append(data[key][1] - data[key][0])
        inlift_times.append(data[key][2] - data[key][1])
    print(f"Algorithm: {algorithm}:")
    print(
        f"\tThe total time waiting for lift is {total_time_waiting_for_lift}. With an average of {total_time_waiting_for_lift / total_users}")
    print(f"\tThe total time in lift is {total_time_in_lift}. With an average of {total_time_in_lift / total_users}")
    print(
        f"\tThe total time spent by users is {total_time_in_lift + total_time_waiting_for_lift}. With an average of {(total_time_in_lift + total_time_waiting_for_lift) / total_users}")
    total_times = [sum(time) for time in zip(waiting_times, inlift_times)]
    # show plots
    #plot_times([waiting_times, inlift_times, total_times] , algorithm) todo fix this

    return waiting_times, inlift_times, total_times

def compare_statistics(simulation_id: int):
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    timing_data = {}
    for key in raw_data["algorithm output"]:
        timing_data[key] = get_statistics_of_algorithm(simulation_id, key)



    # compair each timeing

    # waiting for lift
    plot_compared_times(0, "Waiting for lift comparison", timing_data)
    plot_compared_times(1, "Time in lift comparison", timing_data)
    plot_compared_times(2, "Total time comparison", timing_data)

