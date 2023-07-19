import sys
import pandas as pd
import ast
from os.path import realpath, dirname
from CPM import *
from job_PERT import PJob
from visualize import visualize_PERT, DEAFULT_PATH
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

    makespans = []
    critical_paths = defaultdict(int)
    tmp = {}
    tmp_makespans = defaultdict(list)
    for i in range(10000):
        jobs, CPM_results = cal(jobs_dict)
        earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
        makespans += [makespan]
        critical_paths[str(critical_path)] += 1
        tmp[str(critical_path)] = (jobs, CPM_results)
        tmp_makespans[str(critical_path)].append(makespan)

    plt.figure()
    mean_makespan = np.mean(makespans)
    quantiles = np.quantile(makespans, [0.25, 0.5, 0.75])
    sns.kdeplot(makespans, fill=True)
    plt.title('Density Plot of Makespans')
    plt.xlabel('Makespan')
    plt.savefig(outputpath+'/density_plot.png')

    plt.figure()
    sns.boxplot(makespans, color='lightblue')
    plt.title('Box Plot of Makespans')
    plt.xlabel('Makespan')
    plt.savefig(outputpath+'/box_plot.png')

    
    max_key = max(critical_paths, key=critical_paths.get)
    jobs, CPM_results = tmp[max_key]

    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
    makespan = round(np.average(tmp_makespans[max_key]), 1)
    mode_path_proportion = np.round(critical_paths[max_key]/100, 2)
    print("Mode Critical Path:", critical_path)
    print("Mode Makespan: ", makespan)
    print(f"Mode Path Proportion:  {mode_path_proportion}%")
    CPM_results = (mode_path_proportion, 0, 0, 0, 0, critical_path, makespan)

    visualize_PERT(jobs, CPM_results, outputpath=outputpath)


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