README.txt

Assignment 1 – Advanced Artificial Intelligence Lab (CS5205)

Student Name : Biswaraj Bhattacharyya
Roll No      : 2511AI43
Course       : M.Tech – Artificial Intelligence

------------------------------------------------------------

Problem Description:
This program solves Assignment–1 of the Advanced Artificial Intelligence Lab.
The task is to generate all possible valid schedules to complete a set of
assignments under given constraints.

Each assignment:
- Requires a fixed number of prompts
- May depend on other assignments
- Can be completed only after all its dependencies are satisfied

System constraints:
- There are N students
- Each student has K prompts per day
- A student can solve multiple assignments in a day if prompts allow
- An assignment must be completed in one day by one student only
- All assignments must be completed within m days

------------------------------------------------------------

Input Format:
Input is read from a text file.

- Lines starting with '%' are comments
- N <number>  : Number of students
- K <number>  : Prompts per student per day
- A <id> <prompt_count> <dependencies> 0

Example:
N 3
K 5
A 1 2 0
A 2 4 1 0
A 3 2 2 0

------------------------------------------------------------

How to Run:

Command:
python assg01.py <input-file> <number-of-days>

Example:
python assg01.py input02.txt 3

------------------------------------------------------------

Output:
- All valid schedules that satisfy dependency and prompt constraints
- Output is written to a file named "output.txt"
- The file is overwritten on every run
- Schedules are printed day-wise and student-wise

------------------------------------------------------------

Approach:
- Assignment details are stored using dictionaries
- Dependencies are checked before scheduling an assignment
- A backtracking approach is used to explore all valid schedules
- Prompt limits are enforced per student per day
- Deep copies are used to safely store valid schedules



------------------------------------------------------------

Files Submitted:
- assg01.py  : Python source code
- input01.txt
- input02.txt
- input03.txt        : Sample input files
- output.txt        : Generated output file
- README01.txt        : This file

------------------------------------------------------------

Python Version:
Python 3.x

------------------------------------------------------------
