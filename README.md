# Scheduling Theory

This repository contains code implementations of various scheduling algorithms, used in operations research, computer science, and project management.

## Algorithms Implemented

Currently, the repository contains the following implementations:

- [Critical Path Method (CPM)](./CPM/)
- [Project Evaluation and Review Technique (PERT)](./PERT/)
- [Time/Cost Trade-Offs](./Time_Cost_Trade_Off/)
- [Unpaced Assembly System](./UPAS/)

## Critical Path Method (CPM)
The Critical Path Method (CPM) is a project modeling technique used in project management to identify critical and non-critical tasks and prevent schedule conflicts and bottlenecks.

To get started with the CPM, navigate to the [CPM directory](./CPM/).

## Project Evaluation and Review Technique (PERT)
The Project Evaluation and Review Technique (PERT) is a statistical tool used in project management, designed to analyze and represent the tasks involved in completing a given project. It provides a graphical representation of a project's timeline that allows project managers to identify the critical path of tasks that directly impact the project completion time.

To get started with PERT, navigate to the PERT [directory](./PERT/).

## Time/Cost Trade-Offs
The Time/Cost Trade-Offs method is employed in project management and operations research to find the optimal balance between the time and cost required to complete a project. This method involves analyzing various scenarios where certain tasks within a project can be accelerated at an additional cost. The goal is to determine if the benefits of completing a project ahead of schedule outweigh the additional costs incurred. This trade-off analysis is crucial when there are penalties for late project completion or incentives for early completion.

To delve into the Time/Cost Trade-Offs algorithm, navigate to the Time/Cost Trade-Offs [directory](./Time_Cost_Trade_Off/).

## Unpaced Assembly System (UPAS)
The Unpaced Assembly System (UPAS) is a simulation-based scheduling method that aims to optimize job shop scheduling in a manufacturing setting. The system uses discrete-event simulation to emulate the manufacturing process and derive optimal schedules. The UPAS solver iterates through possible sequences, refining solutions based on an objective function to minimize idle times and maximize efficiency.

The UPAS module is comprehensive, containing preprocessing, simulation, and post-processing steps. This allows users to provide input data, run simulations, and obtain performance metrics seamlessly.

To explore and run the UPAS solver, navigate to the [UPAS directory](./UPAS/).

## Shifting Bottleneck Heuristic
The Shifting Bottleneck Heuristic is a scheduling algorithm used in Job Shop Scheduling Problem. It is designed to optimize the scheduling of tasks by identifying and shifting the bottleneck, which is the resource or task that is causing the longest delay in the project. By focusing on the bottleneck machine, the algorithm aims to improve the overall efficiency and completion time of the project. To learn more about the Shifting Bottleneck Heuristic, refer to the [Shifting Bottleneck Heuristic directory](./Shifting_Bottleneck_Heuristic/).

## Getting Started

To run the code in this repository, you will need Python installed on your machine. You can download Python [here](https://www.python.org/downloads/).

Once you have Python installed, clone this repository to your local machine and navigate into the desired directory.
