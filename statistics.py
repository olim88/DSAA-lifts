import json
from typing import Tuple, List

import matplotlib.pyplot as plt


def plot_times(data: List[List[int]], algorithm: str):
    """
    Uses matplotlib to create a box plot for each aspect of the simulations performance (waiting for lift, in lift, total)
    :param data: a list of lists of values for each of the categories
    :param algorithm: name of the algorithm
    """
    plt.boxplot(data, tick_labels=["Waiting for lift", "In lift", "Total"])

    # Add labels and title
    plt.title(f"Waiting times ({algorithm})")
    plt.ylabel('Time')

    # show
    plt.show()


def plot_compared_times(index: int, name: str, input_data):
    """
     Uses matplotlib to create a box plot for comparison of performance of multiple simulations
    :param index: index of the type of data to show from the input_data
    :param name: the name for the plot
    :param input_data: the data to show in the plot
    """
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
    """
    Loads the output data from the simulation and extract performance statistics
    :param simulation_id: simulation id
    :param algorithm: algorithm name
    :return: a list of data points for how the algorithm performed in (waiting for lift, in lift, total)
    """
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
    """
    Loads the output data from multiple simulations and extract performance statistics
    :param simulation_ids: all simulation ids
    :param algorithm: algorithm name
    :return: a list of data points for how the algorithm performed in (waiting for lift, in lift, total)
    """
    waiting_times = []
    inlift_times = []
    total_times = []
    for sim_id in simulation_ids:
        sim_waiting_times, sim_inlift_times, sim_total_times = get_statistics_of_algorithm(sim_id, algorithm)
        waiting_times.extend(sim_waiting_times)
        inlift_times.extend(sim_inlift_times)
        total_times.extend(sim_total_times)

    return waiting_times, inlift_times, total_times


def show_statistics_of_algorithm(simulation_id: int, algorithm: str):
    """
    Loads then shows statistics about the algorithm performed in (waiting for lift, in lift, total)
    :param simulation_id: simulation id
    :param algorithm: algorithm name
    """
    waiting_times, inlift_times, total_times = get_statistics_of_algorithm(simulation_id, algorithm)
    show_algorithm_statistics(waiting_times, inlift_times, total_times, algorithm)


def show_combined_statistics_of_algorithm(simulation_ids: List[int], algorithm: str):
    """
    Loads then shows statistics about the algorithm performed in (waiting for lift, in lift, total) for multiple simulations
    :param simulation_ids: simulation ids
    :param algorithm: algorithm name
    """
    waiting_times, inlift_times, total_times = get_combined_statistics(simulation_ids, algorithm)
    show_algorithm_statistics(waiting_times, inlift_times, total_times, algorithm)


def show_algorithm_statistics(waiting_times: List[int], inlift_times: List[int], total_times: List[int],
                              algorithm: str):
    """
    Loads and shows statistics from given data
    :param waiting_times: waiting times data points
    :param inlift_times: inlift times data points
    :param total_times: total times data points
    :param algorithm: name of algorithm used
    """
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
    """
    Loads and shows statistics comparing all algorithms run for given simulation id
    :param simulation_id: simulation id
    """
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    timing_data = {}
    if "algorithm output" not in raw_data:
        print("No simulations Run")
        return
    for key in raw_data["algorithm output"]:
        timing_data[key] = get_statistics_of_algorithm(simulation_id, key)

    # waiting for lift
    plot_compared_times(0, "Waiting for lift comparison", timing_data)
    plot_compared_times(1, "Time in lift comparison", timing_data)
    plot_compared_times(2, "Total time comparison", timing_data)
