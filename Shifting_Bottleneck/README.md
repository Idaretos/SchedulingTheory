# Shifting Bottleneck Heuristic

This code implements the shifting bottleneck heuristic algorithm for scheduling jobs on machines. The shifting bottleneck heuristic is used for solving scheduling problems in various domains.

## Installation

No installation is required for this code. Simply clone or download the repository and run the provided Python script.

## Usage

1. Define jobs and machines using `SBJ` and `SBM` classes respectively.
2. Define operations and their durations on respective machines using `SBO` class.
3. Create a scheduling network using the `SBN` class.
4. Call the `shifting_bottleneck` function passing the scheduling network.
5. Plot the resulting schedule using the `plot_graph` method of the scheduling network.

## Example

```python
job1 = SBJ(1, 'job1')
job2 = SBJ(2, 'job2')
job3 = SBJ(3, 'job3')

machine1 = SBM(1, 'machine1')
machine2 = SBM(2, 'machine2')
machine3 = SBM(3, 'machine3')
machine4 = SBM(4, 'machine4')

operation11 = SBO(machine1, job1, 10)
operation21 = SBO(machine2, job1, 8)
operation31 = SBO(machine3, job1, 4)
operation22 = SBO(machine2, job2, 8)
operation12 = SBO(machine1, job2, 3)
operation42 = SBO(machine4, job2, 5)
operation32 = SBO(machine3, job2, 6)
operation13 = SBO(machine1, job3, 4)
operation23 = SBO(machine2, job3, 7)
operation43 = SBO(machine4, job3, 3)

jobs = [job1, job2, job3]
machines = [machine1, machine2, machine3, machine4]

network = SBN(jobs, machines)

network = shifting_bottleneck(network)
network.plot_graph()
