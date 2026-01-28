import sys
import copy

if len(sys.argv) != 3:
    print("Usage: python assgn01_final.py <input-file> <days>")
    sys.exit(1)

filename = sys.argv[1]
max_day = int(sys.argv[2])

def read_input(filename):
    assignments = {}
    N = K = None
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%"):
                continue
            parts = line.split()
            if parts[0] == "N":
                N = int(parts[1])
            elif parts[0] == "K":
                K = int(parts[1])
            elif parts[0] == "A":
                aid = int(parts[1])
                prompts = int(parts[2])
                deps = []
                for d in parts[3:]:
                    if d == "0":
                        break
                    deps.append(int(d))
                assignments[aid] = {"prompts": prompts, "deps": deps}
    return N, K, assignments

def backtrack(day, completed, schedule):
    if len(completed) == len(assignments):
        all_schedules.append(copy.deepcopy(schedule))
        return
    if day > max_day:
        return

    def assign_for_day(student_idx, prompts, daily_tasks, current_completed):
        if student_idx == N:
            if any(daily_tasks[s] for s in daily_tasks):
                schedule[day] = copy.deepcopy(daily_tasks)
                backtrack(day + 1, current_completed.copy(), schedule)
                del schedule[day]
            return

        assign_for_day(student_idx + 1, prompts, daily_tasks, current_completed)

        for aid in assignments:
            if aid in current_completed:
                continue
            if not all(d in current_completed for d in assignments[aid]["deps"]):
                continue
            need = assignments[aid]["prompts"]
            if prompts[student_idx] >= need:
                prompts[student_idx] -= need
                daily_tasks[student_idx].append(aid)
                current_completed.add(aid)
                assign_for_day(0, prompts, daily_tasks, current_completed)
                current_completed.remove(aid)
                daily_tasks[student_idx].pop()
                prompts[student_idx] += need

    assign_for_day(0, [K] * N, {s: [] for s in range(N)}, completed.copy())

N, K, assignments = read_input(filename)
all_schedules = []

with open("output.txt", "w") as output:
    sys.stdout = output
    backtrack(1, set(), {})
    print(f"Total valid schedules: {len(all_schedules)}\n")
    for i, sch in enumerate(all_schedules, 1):
        print(f"Schedule {i}:")
        for d in sorted(sch.keys()):
            print(f" Day {d}:")
            for s in sch[d]:
                print(f"  Student {s}: {sch[d][s]}")
        print("-" * 40)

sys.stdout = sys.__stdout__
print(f"Process complete. Found {len(all_schedules)} schedules.")
