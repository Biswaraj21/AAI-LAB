# Garage Scheduling System

## Description
This project implements a garage scheduling system that assigns repair tasks to multiple mechanics while handling task dependencies, uncertainty, and fatigue constraints.

The system uses:
- Directed Acyclic Graphs (DAGs) for task modeling
- Topological Sorting for execution order
- Simulated Annealing (SA) for optimization
- Monte Carlo Tree Search (MCTS) for dynamic decision making


## Requirements
- Python 3.x

No external libraries required.


## Installation
No installation required.


## How to Run

python main.py -i input1.txt

## Input file

N M k

CAR <TypeName> <num_instances>

TASK <task_id>
TASK <task_id> -> <child>:<probability> <child>:<probability>

N → Number of car types
M → Number of mechanics
k → Max tasks before break