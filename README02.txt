README02.txt

Assignment 2 – Advanced Artificial Intelligence Lab (CS5205)

Student Name : Biswaraj Bhattacharyya
Roll No      : 2511AI43
Course       : M.Tech – Artificial Intelligence

------------------------------------------------------------

Problem Description:
This assignment is an extension of Assignment 1. The goal is to analyze scheduling
feasibility under different constraints by computing optimal parameters instead of
printing all schedules.

The assignment considers a set of assignments with dependencies. Each assignment
requires a fixed number of prompts and must be completed by a single student in one
day. Dependencies must be satisfied before an assignment can be started.

------------------------------------------------------------

Input File Format:
- Lines starting with '%' are comments.
- Assignment format:
  A <assignment_id> <prompt_count> <dependency1> <dependency2> ... 0

Note:
- Group size (N) and prompts per student (K) are NOT read from the input file.
- These values are provided through the command line.

------------------------------------------------------------

Command Line Usage:

python assg02.py <input-file> <mode> <N> <value> [--daily-sync]

Modes:
1. days
   Given:
   - Group size (N)
   - Prompts per student per day (K)
   Output:
   - Earliest number of days required to complete all assignments

   Example:
   python assg02.py input.txt days 3 5

2. prompts
   Given:
   - Group size (N)
   - Number of days (m)
   Output:
   - Minimum number of prompts per student per day required

   Example:
   python assg02.py input.txt prompts 3 2

------------------------------------------------------------

6 AM Solution Exchange Rule (Assignment 2 – Part 3):

By default, assignments can use solutions of their prerequisite tasks completed
earlier on the SAME day.

To enable the special rule where students exchange solutions only at 6 am on the
NEXT day, use the optional flag:

--daily-sync

Example:
python assg02.py input.txt days 3 5 --daily-sync

Behavior with --daily-sync:
- Dependencies are checked only against assignments completed on previous days.
- Same-day dependency execution is NOT allowed.

------------------------------------------------------------

Approach Used:
- A backtracking-based feasibility checker is used.
- Instead of printing all schedules, the program checks whether at least one valid
  schedule exists under given constraints.
- For Part 1, the number of days is incremented until a feasible schedule is found.
- For Part 2, the prompt count is incremented until a feasible schedule is found.
- State copying is used to avoid corruption during recursive backtracking.

The approach is brute-force but simple and suitable for academic demonstration.

------------------------------------------------------------

Files Submitted:
- assg02.py     : Python source code
- input.txt     : Assignment input file(s)
- README02.txt  : This file

------------------------------------------------------------

Python Version:
Python 3.x

------------------------------------------------------------
