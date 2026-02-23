README04.txt

Assignment 4 – Advanced Artificial Intelligence Lab (CS5205)

Student Name : Biswaraj Bhattacharyya
Roll No      : 2511AI43
Course       : M.Tech – Artificial Intelligence

------------------------------------------------------------

Problem Description:

This assignment models and solves an Electric Vehicle (EV) charging
scheduling problem using Z3 Optimize (SMT Solver).

Given:
- K charging ports
- Different pricing for each port
- Vehicles with arrival time, departure time, and required charge

The objective is to:
1) Assign each vehicle to exactly one port
2) Schedule charging within its time window
3) Ensure no two vehicles overlap on the same port
4) Minimize the total charging cost

The problem is formulated as a constraint optimization problem and
solved using Z3's Optimize() engine.

------------------------------------------------------------

Input File Format:

The input file consists of:

K <number_of_ports>
P <price_port1> <price_port2> ... <price_portK>
V <vehicle_id> <arrival_time> <departure_time> <charge_required>

Example:

% number of ports
K 3

% price per port
P 5 3 2

% vehicles
V 1 0 10 8
V 2 2 12 6
V 3 5 15 10

Explanation:
- K = number of charging ports
- P = cost per unit time for each port
- V = vehicle information

------------------------------------------------------------

Model Description:

For each vehicle i:
- port_i  : Integer variable (1 to K)
- start_i : Charging start time
- end_i   : Charging end time

Constraints:

1) Port Assignment:
   1 ≤ port_i ≤ K

2) Charging Time:
   charging_time = ceil(charge_required / port_number)
   end_i = start_i + charging_time

3) Time Window:
   arrival_i ≤ start_i
   end_i ≤ departure_i

4) No Overlapping on Same Port:
   If two vehicles share the same port,
   then their charging intervals must not overlap.

5) Objective:
   Minimize total cost:
   cost = Σ (price_of_port × charging_time)

The optimization is performed using:
   opt = Optimize()
   opt.minimize(total_cost)

------------------------------------------------------------

How to Run:

python schedule.py <input-file>

Example:

python schedule.py input.txt

------------------------------------------------------------

Output:

If a feasible optimal schedule is found, the program prints:

- Total minimum cost
- For each vehicle:
    - Assigned port
    - Charging start time
    - Charging end time

If no solution exists:
    "No feasible schedule found"

------------------------------------------------------------

Approach Used:

- The problem is encoded as an SMT optimization model.
- Integer variables represent port selection and timing.
- Z3's Optimize() is used to minimize total charging cost.
- Ceiling division is handled using Python's math.ceil().
- Non-overlapping constraints are modeled using logical OR.

------------------------------------------------------------

Files Submitted:

- schedule.py   : Python source code (Z3-based model)
- input.txt     : Test input file(s)
- README04.txt  : This file

------------------------------------------------------------

Software Requirements:

- Python 3.x
- Z3 Solver (Python API)

Install Z3 using:
pip install z3-solver

------------------------------------------------------------