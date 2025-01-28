import json

if __name__ == '__main__':
    # open output data file
    with open("data/output.json", "r") as f:
        data = json.load(f)

    # extract statistics from the data
    total_time_waiting_for_lift = 0
    total_time_in_lift = 0
    total_users = len(data)
    for key in data:
        total_time_waiting_for_lift += data[key][1] - data[key][0]
        total_time_in_lift += data[key][2] - data[key][1]


    print(f"The total time waiting for lift is {total_time_waiting_for_lift}. With an average of {total_time_waiting_for_lift/total_users}")
    print(f"The total time in lift is {total_time_in_lift}. With an average of {total_time_in_lift/total_users}")
