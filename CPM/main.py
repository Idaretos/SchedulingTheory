from CPM import *
from visualize import visualize_CPM

if __name__ == '__main__':
    jobs = {1: Job('1', 4, predecessors=[]), 
            2: Job('2', 6, predecessors=[]), 
            3: Job('3', 10, predecessors=[]), 
            4: Job('4', 12, predecessors=[1]), 
            5: Job('5', 10, predecessors=[2]), 
            6: Job('6', 2, predecessors=[3, 4, 5]), 
            7: Job('7', 4, predecessors=[3, 4]), 
            8: Job('8', 2, predecessors=[6, 7])}
 
    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path = cpm_algorithm(
        network
    )

    # Print the results
    print("Earliest Start Time:", earliest_start_time)
    print("Earliest Finish Time:", earliest_finish_time)
    print("Latest Start Time:", latest_start_time)
    print("Latest Finish Time:", latest_finish_time)
    print("Slacks:", slacks)
    print("Critical Path:", critical_path)
    print("Makespan: ", max(earliest_finish_time.values()))

    visualize_CPM(jobs, critical_path)
