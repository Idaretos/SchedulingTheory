import sys
import json
from os.path import realpath, dirname
from CPM import *
from job_PERT import PJob
from visualize import visualize_CPM, DEAFULT_PATH
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import defaultdict

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
    
    makespans = []
    critical_paths = defaultdict(int)
    tmp = {}
    for i in range(1000):
        jobs, CPM_results = cal(jobs_dict)
        earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
        makespans += [makespan]
        critical_paths[str(critical_path)] += 1
        tmp[str(critical_path)] = (jobs, CPM_results)

    plt.figure()
    mean_makespan = np.mean(makespans)
    quantiles = np.quantile(makespans, [0.25, 0.5, 0.75])
    sns.kdeplot(makespans, fill=True)
    plt.title('Density Plot of Makespans')
    plt.xlabel('Makespan')
    plt.savefig(DEAFULT_PATH+'/density_plot.png')

    plt.figure()
    sns.boxplot(makespans, color='lightblue')
    plt.title('Box Plot of Makespans')
    plt.xlabel('Makespan')
    plt.savefig(DEAFULT_PATH+'/box_plot.png')


    max_key = max(critical_paths, key=critical_paths.get)
    print(max_key, critical_paths[max_key]/1000)
    jobs, CPM_results = tmp[max_key]
    visualize_CPM(jobs, CPM_results)


def cal(jobs_dict):
    # Convert the dictionary back to Job objects
    jobs = {id: PJob(**job_data) for id, job_data in jobs_dict.items()}

    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    CPM_results = CPM(network)
    return jobs, CPM_results

if __name__ == '__main__':
    main()