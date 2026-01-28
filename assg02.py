import sys
import copy

if len(sys.argv) < 5:
    print("Usage:")
    print("python assg02.py <input-file> <days|prompts> <N> <value> [--daily-sync]")
    sys.exit(1)

filename = sys.argv[1]
mode = sys.argv[2]
N = int(sys.argv[3])
value = int(sys.argv[4])
daily_sync = "--daily-sync" in sys.argv

def read_input(filename):
    assignments = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if parts[0] == "A":
                aid = int(parts[1])
                prompts = int(parts[2])
                deps = []
                for d in parts[3:]:
                    if d == "0":
                        break
                    deps.append(int(d))
                assignments[aid] = {"prompts": prompts, "deps": deps}
    return assignments

def backtrack(day, max_day, completed, schedule, assignments, K):
    if len(completed) == len(assignments):
        return True

    if day > max_day:
        return False

    def assign_for_day(student_idx, prompts, daily_tasks, current_completed):
        if student_idx == N:
            if any(daily_tasks[s] for s in daily_tasks):
                next_completed = current_completed.copy()
                return backtrack(day + 1, max_day, next_completed,
                                 schedule, assignments, K)
            return False

        if assign_for_day(student_idx + 1, prompts, daily_tasks, current_completed):
            return True

        for aid in assignments:
            if aid in current_completed:
                continue

            deps_ok = all(
                d in completed if daily_sync else d in current_completed
                for d in assignments[aid]["deps"]
            )
            if not deps_ok:
                continue

            need = assignments[aid]["prompts"]
            if prompts[student_idx] >= need:
                prompts[student_idx] -= need
                daily_tasks[student_idx].append(aid)
                current_completed.add(aid)

                if assign_for_day(0, prompts, daily_tasks, current_completed):
                    return True

                current_completed.remove(aid)
                daily_tasks[student_idx].pop()
                prompts[student_idx] += need

        return False

    return assign_for_day(
        0,
        [K] * N,
        {s: [] for s in range(N)},
        completed.copy()
    )

assignments = read_input(filename)

# ---------- PART 1 ----------
if mode == "days":
    K = value
    day = 1
    while True:
        if backtrack(day, day, set(), {}, assignments, K):
            print(f"Earliest completion time = {day} days")
            break
        day += 1

# ---------- PART 2 ----------
elif mode == "prompts":
    max_day = value
    K = 1
    while True:
        if backtrack(1, max_day, set(), {}, assignments, K):
            print(f"Minimum prompts per student per day = {K}")
            break
        K += 1

else:
    print("Invalid mode. Use 'days' or 'prompts'.")
