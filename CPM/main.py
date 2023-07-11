import sys
import json
from CPM import *
from visualize import visualize_CPM, DEAFULT_PATH

def main():
    if len(sys.argv) > 1:
        inputpath = sys.argv[1]
    if len(sys.argv) > 2:
        outputpath = sys.argv[2]
    else:
        inputpath = 'SchedulingTheory/CPM/input/lecture.json'
        outputpath = DEAFULT_PATH

    with open(inputpath, 'r') as f:
        jobs_dict = json.load(f)

    # Convert the dictionary back to Job objects
    jobs = {int(id): Job(**job_data) for id, job_data in jobs_dict.items()}

    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path = cpm_algorithm(network)

    # Print the results
    print("Earliest Start Time:", earliest_start_time)
    print("Earliest Finish Time:", earliest_finish_time)
    print("Latest Start Time:", latest_start_time)
    print("Latest Finish Time:", latest_finish_time)
    print("Slacks:", slacks)
    print("Critical Path:", critical_path)
    print("Makespan: ", max(earliest_finish_time.values()))

    visualize_CPM(jobs, critical_path, outputpath)

if __name__ == '__main__':
    main()