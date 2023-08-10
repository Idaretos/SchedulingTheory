# Time/Cost Trade-Offs
This project provides an in-depth analysis and implementation of time/cost trade-offs in project management. Leveraging the Critical Path Method (CPM) and advanced optimization techniques, this framework evaluates tasks within a project and fine-tunes them according to specified rules.

## Files

- `Jobs.py`: Contains the definition of the `Job` class, which encapsulates individual tasks or activities in a project.
- `AdjacencyTable.py`: Houses the `AdjacencyTable` class, a tool for representing and managing relationships between different jobs using a graph structure.
- `CPM_visualize.py`: Features visualization functions, allowing users to graphically represent the job network, critical paths, and other pertinent information.
- `Optimizer.py`: Introduces the `Optimizer` class which, building upon the functionalities from the `PathFinder` class, offers methods for optimizing job paths through heuristic or linear strategies.
- `preprocessing.py`: A utility file that likely incorporates functions or classes essential for data preparation or transformation before its main processing phase.
- `main.py`: Serves as the application's primary entry point. It integrates functionalities from the other modules, processes command-line arguments, and executes the optimization and visualization processes.

## Usage

To use this program, you must first provide csv files with the job data.
Here is an example of the data file format:

`workflow.csv`: This file provides the job workflow information, detailing the dependencies between the tasks.
```csv
id,predecessors
1,[]
2,[1]
3,[]
4,[]
5,[3]
6,[4]
7,[4]
8,"[1, 5, 6]"
9,"[1, 5, 6]"
10,[2]
11,"[7, 8, 9]"
```

`costs.csv`: This file provides the cost and time details of each job.
```csv
job,p_max,p_min,min_cost,marginal_cost,overhead_cost
1,8,5,30,7,6
2,5,3,25,2
3,6,4,20,2
4,3,2,15,1
5,2,2,30,2
6,5,3,40,3
7,2,2,35,4
8,4,3,25,4
9,7,5,30,4
10,4,3,20,5
11,9,7,30,4
```

To execute the program:

1. Ensure you have your data files prepared. The specifics of the file format will be based on the requirements of the `read_files` function from the `preprocessing` module.
2. Run the `main.py` script with the necessary command-line arguments. Example:

```bash
python main.py 'path_to_data_file' 'optimization_rule' 'visualization_flag'
```
Where:
- <path_to_data_file> is the path to your input data file.
- <optimization_rule> can be either 'heuristic' or 'linear' based on your preference.
- <visualization_flag> is a boolean (or similar indicator) to specify if visualization should be generated.

The script will process the input, execute the optimization, and display the results as needed.

## Output
The program will analyze the job data and output the following results:
`heuristic`:
```txt
job:    1       2       3       4       5       6       7       8       9       10      11
p_max:  8       5       6       3       2       5       2       4       7       4       9
p_min:  5       3       4       2       2       3       2       3       5       3       7
cost:   51      29      24      16      30      46      35      29      30      25      30
marg:   7       2       2       1       2       3       4       4       4       5       4
dur:    8       5       6       3       2       5       2       4       5       4       7
critical_paths:
  source -> 1 -> 9 -> 11 -> sink
  source -> 3 -> 5 -> 9 -> 11 -> sink
  source -> 4 -> 6 -> 9 -> 11 -> sink
total_cost: 345
makespan: 20
```

`linear`:
```txt
Start times: [0.0, 8.0, 0.0, 0.0, 6.0, 3.0, 3.0, 8.0, 8.0, 16.0, 13.0]
Processing times: [8.0, 5.0, 6.0, 3.0, 2.0, 5.0, 2.0, 4.0, 5.0, 4.0, 7.0]
Costs: [51.0, 29.0, 24.0, 16.0, 30.0, 46.0, 35.0, 29.0, 30.0, 25.0, 30.0]
Makespan: 20.0
```

## Dependencies
For a smooth operation of this project, ensure you have the following Python libraries installed:

- `os`
- `numpy`
- `pandas`
- `itertools`
- `pulp`
- `matplotlib`
- `networkx`
- `pygraphviz`
- `collections`

Furthermore, the necessary modules(`Jobs`, `AdjacencyTable`, `CPM_visualize`, and others) should be accessible either in the project directory or within your Python's path.

## Notes
- The exact specifications, especially for the input data format and command-line arguments, might vary based on the internal workings of the preprocessing and Optimizer modules. It's recommended to consult these modules or related documentation for detailed instructions.