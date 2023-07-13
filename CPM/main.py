import sys
import json
from os.path import realpath, dirname
from CPM import *
from visualize import visualize_CPM, DEAFULT_PATH

def main():
    if len(sys.argv) > 1:
        inputpath = sys.argv[1]
    if len(sys.argv) > 2:
        outputpath = sys.argv[2]
    else:
        inputpath = dirname(realpath(__file__))+'/input/example.json'
        outputpath = DEAFULT_PATH

    with open(inputpath, 'r') as f:
        jobs_dict = json.load(f)

    # Convert the dictionary back to Job objects
    jobs = {id: Job(**job_data) for id, job_data in jobs_dict.items()}

    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    CPM_results = CPM(network)
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
    # Print the results
    print("Earliest Start Time:", earliest_start_time)
    print("Earliest Finish Time:", earliest_finish_time)
    print("Latest Start Time:", latest_start_time)
    print("Latest Finish Time:", latest_finish_time)
    print("Slacks:", slacks)
    print("Critical Path:", critical_path)
    print("Makespan: ", makespan)

    visualize_CPM(jobs, CPM_results, outputpath)

if __name__ == '__main__':
    main()