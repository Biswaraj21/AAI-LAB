import sys

sys.setrecursionlimit(5000)

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
                    assignments[aid] = {"prompts": prompts, "deps": deps}
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)
    return assignments

def can_solve(max_days, prompts_per_student, num_students, assignments, daily_sync):
    memo = {}

    def backtrack(day, completed_before_today):
        if len(completed_before_today) == len(assignments):
            return True

        if day > max_days:
            return False

        state = (day, tuple(sorted(completed_before_today)))
        if state in memo:
            return memo[state]

        def solve_day(student_capacities, current_day_done):
            possible_tasks_found = False
            
            for aid, data in assignments.items():
                if aid not in completed_before_today and aid not in current_day_done:
                   
                    if daily_sync:
                        deps_met = all(d in completed_before_today for d in data["deps"])
                    else:
                        deps_met = all(d in completed_before_today or d in current_day_done for d in data["deps"])

                    if deps_met:
                        needed = data["prompts"]
                        for s in range(num_students):
                            if student_capacities[s] >= needed:
                                possible_tasks_found = True
                                
                                student_capacities[s] -= needed
                                current_day_done.add(aid)
                                
                                if solve_day(student_capacities, current_day_done):
                                    return True
                                
                                current_day_done.remove(aid)
                                student_capacities[s] += needed

            return backtrack(day + 1, completed_before_today | current_day_done)

        res = solve_day([prompts_per_student] * num_students, set())
        memo[state] = res
        return res

    return backtrack(1, set())

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python assg02.py <input-file> <days|prompts> <N> <value> [--daily-sync]")
        sys.exit(1)

    filename = sys.argv[1]
    mode = sys.argv[2]
    N = int(sys.argv[3])
    val = int(sys.argv[4])
    daily_sync_flag = "--daily-sync" in sys.argv

    data = read_input(filename)

    if mode == "days":
        K = val
        d = 1
        while d <= len(data) * 2:
            if can_solve(d, K, N, data, daily_sync_flag):
                print(f"Earliest completion time = {d} days")
                break
            d += 1

    elif mode == "prompts":
        D = val
        low = 1
        high = sum(a["prompts"] for a in data.values())
        ans = high
        
        while low <= high:
            mid = (low + high) // 2
            if mid == 0: 
                low = 1
                continue
            if can_solve(D, mid, N, data, daily_sync_flag):
                ans = mid
                high = mid - 1
            else:
                low = mid + 1
        print(f"Minimum prompts per student per day = {ans}")