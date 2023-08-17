# Scheduling Theory - Unpaced Assembly System (UPAS)
This project simulates an Unpaced Assembly System to optimize job shop scheduling. The system uses the SimPy discrete-event simulation library to emulate the manufacturing process and determine optimal schedules.

## Files
- `Preprocessing.py`: Contains functions for preprocessing input data and preparing it for the simulation.
- `simulation.py`: Houses the core simulation classes and logic, including representations for parts, machines, sources, and sinks. It also contains a monitoring system for logging events.
- `model.py`: The main script that initializes and runs the simulation, and then logs results.
- `PostProcessing.py`: Offers functions for post-processing the simulation data and computing key performance metrics.
- `UPAS_Solver.py`: Provides a solver for the Unpaced Assembly System. This script combines preprocessing, simulation, and post-processing steps to find an optimal job sequence that minimizes a defined objective function.
- `main.py`: Executes the UPAS Solver based on provided command-line arguments for the input data path and the starting job.

## Usage
Using the `main.py` script:

Provide the input data path and optionally the first job as command-line arguments.
bash

```bash
python main.py path_to_input_data.csv 0
```

This will initialize the `UPAS_Solver class`, execute the solver, and display the results.

To use this program, you must first provide txt files with the job and machine data.
Here is an example of the data file format:

```txt
num_jobs    num_machines
operation times for m1
operation times for m2
... (for each machine)
weight for each machine.
```
```txt
3   4
1   1   1
0   1   0
0   0   0
1   0   1
1   1   0
1   1   1   1
```

## Results

The simulation provides insights into the scheduling of jobs within the Unpaced Assembly System. The `Monitor` object in `simulation.py` maintains an event log detailing various events such as part creation, operation starts/finishes, and part transfers.

The `UPAS_Solver` aims to find the optimal sequence of jobs by simulating different sequences and evaluating their performance based on the objective function. The solver iteratively explores possible sequences, progressively refining the solution.

## Dependencies
Ensure you have all the necessary libraries installed:
- `simpy`
- `pandas`