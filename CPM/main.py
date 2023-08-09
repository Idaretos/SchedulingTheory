import pandas as pd
import sys
import ast
from os.path import realpath, dirname
from visualize import *
from CPM import *

def main():
    if len(sys.argv) > 1:
        inputpath = sys.argv[1]
    if len(sys.argv) > 2:
        outputpath = sys.argv[2]
    else:
        inputpath = dirname(realpath(__file__))+'/input/example.csv'
        outputpath = DEAFULT_PATH

    df = pd.read_csv(inputpath)

    # Convert the "predecessors" column to a list
    df['predecessors'] = df['predecessors'].apply(ast.literal_eval)
    df['id'] = df['id'].apply(str)

    # Convert the DataFrame to a dictionary
    jobs_dict = df.to_dict('index')
    
    # Convert the keys to 'id'
    jobs_dict = {value['id']: value for key, value in jobs_dict.items()}

    # Convert the dictionary to Job objects
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
    # print("Critical Path:", critical_path)
    print_critical_paths(network, title='Critical Paths')
    print("Makespan: ", makespan)

    visualize_CPM(jobs, CPM_results, network, outputpath)

if __name__ == '__main__':
    main()