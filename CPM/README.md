# Scheduling Theory - Critical Path Method (CPM)
This project implements the Critical Path Method (CPM), a popular algorithm in scheduling theory. CPM is commonly used in project management for scheduling a set of project activities.

## Files

- `CPM.py`: This file contains the implementation of the CPM algorithm, with classes defined for Job and Network, and various functions for calculating earliest times, latest times, slacks and the critical path.

- `visualize.py`: This file contains the code for visualizing the network of jobs using networkx and matplotlib. It creates a directed graph based on job states and illustrates critical and non-critical paths in the project network. The output is saved as a PNG file.

- `main.py`: This is the main script that you run to execute the program. It defines the jobs and dependencies, creates the network, runs the CPM algorithm, prints the results, and visualizes the job network.

## Usage

To use this program, you must first provide a csv file with the job data.
Here is an example of the data file format:

```csv
|   id |   duration | predecessors   |
|-----:|-----------:|:---------------|
|    1 |          5 | []             |
|    2 |          6 | [1]            |
|    3 |          9 | [1]            |
|    4 |         12 | [2]            |
|    5 |          7 | [3]            |
|    6 |         12 | [3]            |
|    7 |         10 | [4]            |
|    8 |          6 | [5, 6]         |
|    9 |         10 | [5, 6]         |
|   10 |          9 | [7]            |
|   11 |          7 | [8, 9]         |
|   12 |          8 | [10, 11]       |
|   13 |          7 | [11]           |
|   14 |          5 | [12, 13]       |
```

To run the program, execute the main.py script. Make sure you have all the required dependencies installed.

```bash
python main.py 'input_filename' 'output_directory'
```
The program will read the `.json` file and runs `CPM`. You should see the output of the CPM algorithm in the console, and a PNG file named `CPM.png` will be created in the output directory, visualizing the job network.

![image not found](output/example_CPM.png)

## Dependencies

This project requires the following Python libraries:

- `networkx`
- `matplotlib`
- `pygraphviz`
- `collections`
- `json`
