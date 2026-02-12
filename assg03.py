import sys
import heapq
import itertools
import time


sys.setrecursionlimit(10000)

def read_input(filename):
    assignments = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("%"):
                    continue
                parts = line.split()
                if parts[0] == "A":
                    aid = int(parts[1])
                    prompts = int(parts[2])
                    deps = [int(d) for d in parts[3:] if d != "0"]
               
                    llm_type = 0 if aid % 2 == 0 else 1 
                    assignments[aid] = {"prompts": prompts, "deps": deps, "llm": llm_type}
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    return assignments

def get_h(assignments, completed_tasks):
    memo = {}
    remaining = [aid for aid in assignments if aid not in completed_tasks]
    if not remaining: return 0

    def get_depth(aid):
        if aid in completed_tasks: return 0
        if aid in memo: return memo[aid]
        max_d = 0
        for dep in assignments[aid]['deps']:
            max_d = max(max_d, get_depth(dep))
        memo[aid] = 1 + max_d
        return memo[aid]

    return max(get_depth(aid) for aid in remaining)

def get_options(assignments, completed_before, n_students, p_limits, case):
    available = [aid for aid, data in assignments.items() 
                 if aid not in completed_before and all(d in completed_before for d in data['deps'])]
    
    valid_combos = []
    def backtrack(idx, current_set, p_used, s_used):
        if idx == len(available):
            if current_set: valid_combos.append(set(current_set))
            return
        
        aid = available[idx]
        data = assignments[aid]
        llm, cost = data['llm'], data['prompts']

        can_fit = p_used[llm] + cost <= p_limits[llm]
        if case == 'A' and s_used >= n_students: can_fit = False

        if can_fit:
            p_next = list(p_used)
            p_next[llm] += cost
            backtrack(idx + 1, current_set + [aid], p_next, s_used + 1)
        backtrack(idx + 1, current_set, p_used, s_used)

    backtrack(0, [], [0, 0], 0)
    return sorted(valid_combos, key=len, reverse=True)

class Solver:
    def __init__(self, assignments, n_students, case):
        self.assignments = assignments
        self.n_students = n_students
        self.case = case
        self.nodes = 0

    def solve_a_star(self, p_limits):
        self.nodes = 0
        pq = [(get_h(self.assignments, set()), 0, tuple())]
        visited = {tuple(): 0}
        
        while pq:
            f, g, current = heapq.heappop(pq)
            self.nodes += 1
            if len(current) == len(self.assignments): return g
            
            for opt in get_options(self.assignments, set(current), self.n_students, p_limits, self.case):
                new_state = tuple(sorted(list(set(current) | opt)))
                if new_state not in visited or g + 1 < visited[new_state]:
                    visited[new_state] = g + 1
                    h = get_h(self.assignments, set(new_state))
                    heapq.heappush(pq, (g + 1 + h, g + 1, new_state))
        return float('inf')

    def solve_dfbb(self, p_limits, deadline=float('inf')):
        self.nodes = 0
        self.best_g = deadline
        
        def dfs(current, g):
            self.nodes += 1
            if len(current) == len(self.assignments):
                self.best_g = min(self.best_g, g)
                return
            
            h = get_h(self.assignments, set(current))
            if g + h >= self.best_g: return

            for opt in get_options(self.assignments, set(current), self.n_students, p_limits, self.case):
                dfs(tuple(sorted(list(set(current) | opt))), g + 1)

        dfs(tuple(), 0)
        return self.best_g if self.best_g != deadline else float('inf')

def objective_two(solver, deadline, c1, c2):
    """Finds best subscription scheme (min daily cost)[cite: 18]."""
    min_cost = float('inf')
    best_p = (0, 0)
    max_range = sum(a['prompts'] for a in solver.assignments.values())
    
    for pc in range(1, max_range):
        for pg in range(1, max_range):
            cost = (pc * c1) + (pg * c2) # 
            if cost >= min_cost: continue
            if solver.solve_a_star([pc, pg]) <= deadline:
                min_cost = cost
                best_p = (pc, pg)
    return best_p, min_cost

if __name__ == "__main__":
    data = read_input(sys.argv[1])
    case, students = sys.argv[2].upper(), int(sys.argv[3])
    mode = sys.argv[4].lower()
    s = Solver(data, students, case)

    if mode == "earliest":
        p_lims = [int(sys.argv[5]), int(sys.argv[6])]
        res_a = s.solve_a_star(p_lims)
        nodes_a = s.nodes
        res_dfbb = s.solve_dfbb(p_lims)
        print(f"Earliest Finish: {res_a} days\nA* Nodes: {nodes_a}, DFBB Nodes: {s.nodes}")

    elif mode == "mincost":
        deadline, c1, c2 = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
        scheme, total = objective_two(s, deadline, c1, c2)
        print(f"Min Subscription: ChatGPT={scheme[0]}, Gemini={scheme[1]} | Daily Cost={total}")