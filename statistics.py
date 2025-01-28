import json
import matplotlib.pyplot as plt




def plot_times(data):
    plt.boxplot(data, tick_labels=["Waiting for lift", "In lift", "Total"])

    # Add labels and title
    plt.title(f"Waiting times")
    plt.ylabel('Time')

    #show
    plt.show()


if __name__ == '__main__':
    # open output data file
    with open("data/output.json", "r") as f:
        data = json.load(f)

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



    print(f"The total time waiting for lift is {total_time_waiting_for_lift}. With an average of {total_time_waiting_for_lift/total_users}")
    print(f"The total time in lift is {total_time_in_lift}. With an average of {total_time_in_lift/total_users}")
    print(f"The total time spent by users is {total_time_in_lift + total_time_waiting_for_lift}. With an average of {(total_time_in_lift + total_time_waiting_for_lift)/ total_users}")

    #show plots
    plot_times([wating_times, inlift_times, [sum(time) for time in zip(wating_times, inlift_times)]])

