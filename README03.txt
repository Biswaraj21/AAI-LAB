README02.txt

Assignment 3 – Advanced Artificial Intelligence Lab (CS5205)

Student Name : Biswaraj Bhattacharyya
Roll No      : 2511AI43
Course       : M.Tech – Artificial Intelligence

------------------------------------------------------------

Problem Description:
This program solves Assignment-2 using informed search techniques.
Each assignment has:
- A prompt requirement (cost)
- Dependency constraints
- An LLM type requirement:
    Even assignment ID  -> ChatGPT (type 0)
    Odd assignment ID   -> Gemini  (type 1)

The objective is solved for two cases:
Case A: Limited number of students (max tasks per day = N)
Case B: Unlimited students (only prompt limits apply)

The program supports:
1) Finding earliest completion time (minimum days) using:
   - A* Search
   - DFBB (Depth First Branch and Bound)

2) Finding the minimum daily subscription cost (ChatGPT + Gemini)
   such that all tasks finish within a given deadline.

------------------------------------------------------------

Input Format:
The input file contains only assignment lines (comment lines allowed):

% comment
A <id> <prompt_cost> <dep1> <dep2> ... 0

Example:
A 1 3 0
A 2 4 1 0
A 3 2 2 0

Note:
- Dependency list ends at 0.
- N and K are NOT read from the file.

------------------------------------------------------------

How to Run:

General format:
python assg03.py <input-file> <case> <students> <mode> <parameters...>

Where:
case     : A or B
students : number of students (used only for Case A)
mode     : earliest OR mincost

------------------------------------------------------------

MODE 1: earliest
Goal: Find the minimum number of days required.

Command:
python assg03.py <input-file> <case> <students> earliest <P_chatgpt> <P_gemini>

Example:
python assg03.py input.txt A 3 earliest 10 12

Output:
- Earliest finish time in days
- Nodes expanded by A*
- Nodes expanded by DFBB

------------------------------------------------------------

MODE 2: mincost
Goal: Find the minimum daily subscription scheme such that all assignments
finish within a given deadline.

Command:
python assg03.py <input-file> <case> <students> mincost <deadline> <c1> <c2>

Where:
deadline : maximum allowed days
c1       : cost per ChatGPT prompt
c2       : cost per Gemini prompt

Example:
python assg03.py input.txt B 3 mincost 5 2 3

Output:
- Minimum (ChatGPT prompts, Gemini prompts) subscription scheme
- Minimum daily cost

------------------------------------------------------------

Approach Used:
1) A* Search:
   - State = set of completed assignments
   - Each action = selecting a valid subset of available assignments for a day
   - g(n) = days used so far
   - h(n) = maximum dependency depth remaining (admissible heuristic)

2) DFBB:
   - Depth-first exploration with pruning using:
     g(n) + h(n) >= best_solution

3) Subscription Optimization:
   - Brute force search over possible daily prompt limits
   - Chooses the cheapest scheme that finishes within deadline

------------------------------------------------------------

Files Submitted:
- assg03.py     : Python source code
- input.txt     : Assignment input file(s)
- README03.txt  : This file

------------------------------------------------------------

Python Version:
Python 3.x

------------------------------------------------------------
