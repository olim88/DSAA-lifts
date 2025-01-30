import json
import matplotlib.pyplot as plt




def plot_times(data, algorithm :str):
    plt.boxplot(data, tick_labels=["Waiting for lift", "In lift", "Total"])

    # Add labels and title
    plt.title(f"Waiting times ({algorithm})")
    plt.ylabel('Time')

    #show
    plt.show()

def get_statistics(simulation_id: int, algorithm: str):
    # open output data file
    with open(f"simulations/simulation_{simulation_id}.json", "r") as f:
        raw_data = json.load(f)
    #get data for chosen algorithm
    if algorithm not in raw_data:
        raise Exception(f"Algorithm {algorithm} not found.")
    data = raw_data[algorithm]
    # extract statistics from the data
    total_time_waiting_for_lift = 0
    wating_times = []
    total_time_in_lift = 0
    inlift_times = []
    total_users = len(data)
    for key in data:
        total_time_waiting_for_lift += data[key][1] - data[key][0]
        total_time_in_lift += data[key][2] - data[key][1]
        wating_times.append(data[key][1] - data[key][0])
        inlift_times.append(data[key][2] - data[key][1])
    print(f"Algorithm: {algorithm}:")
    print(
        f"\tThe total time waiting for lift is {total_time_waiting_for_lift}. With an average of {total_time_waiting_for_lift / total_users}")
    print(f"\tThe total time in lift is {total_time_in_lift}. With an average of {total_time_in_lift / total_users}")
    print(
        f"\tThe total time spent by users is {total_time_in_lift + total_time_waiting_for_lift}. With an average of {(total_time_in_lift + total_time_waiting_for_lift) / total_users}")

    # show plots
    plot_times([wating_times, inlift_times, [sum(time) for time in zip(wating_times, inlift_times)]], algorithm)

