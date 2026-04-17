import sys
import re
import random
import argparse
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Task:
    """One node in a car-type DAG."""

    task_id: str  
    car_inst: str 
    is_spawn: bool = False

    def label(self) -> str:
        tag = " [spawn]" if self.is_spawn else ""
        return f"{self.task_id}({self.car_inst}){tag}"


@dataclass
class Edge:

    parent_id: str
    child_id: str
    probability: float  # threshold in [0.0, 1.0]

    def __repr__(self):
        return f"{self.parent_id} --({self.probability:.2f})--> {self.child_id}"


@dataclass
class CarTypeDAG:


    type_name: str
    tasks: dict = field(default_factory=dict) 
    edges: list = field(default_factory=list) 
    children: dict = field(default_factory=dict) 


    def add_task(self, task_id: str):
        if task_id not in self.tasks:
            self.tasks[task_id] = Task(task_id=task_id, car_inst="?")
            self.children[task_id] = []

    def add_edge(self, parent_id: str, child_id: str, prob: float):
        self.add_task(parent_id)
        self.add_task(child_id)
        e = Edge(parent_id=parent_id, child_id=child_id, probability=prob)
        self.edges.append(e)
        self.children[parent_id].append(e)

    def roots(self) -> list:
        has_parent = {e.child_id for e in self.edges}
        return [tid for tid in self.tasks if tid not in has_parent]

    def topological_order(self) -> list:
        in_deg = {tid: 0 for tid in self.tasks}
        for e in self.edges:
            in_deg[e.child_id] += 1
        queue = deque(tid for tid, d in in_deg.items() if d == 0)
        order = []
        while queue:
            tid = queue.popleft()
            order.append(tid)
            for e in self.children[tid]:
                in_deg[e.child_id] -= 1
                if in_deg[e.child_id] == 0:
                    queue.append(e.child_id)
        if len(order) != len(self.tasks):
            raise ValueError(
                f"[{self.type_name}] DAG contains a cycle — " "topological sort failed."
            )
        return order

    def display(self, indent: str = "  ") -> str:
        lines = [f"{indent}Car type : {self.type_name}"]
        lines.append(f"{indent}Tasks (adjacency list):")
        for tid in self.topological_order():
            kids = self.children[tid]
            if kids:
                child_str = "  ->  " + "  ".join(
                    f"{e.child_id}:{e.probability:.2f}" for e in kids
                )
            else:
                child_str = "  (leaf)"
            lines.append(f"{indent}  TASK {tid:<8}{child_str}")
        return "\n".join(lines)


@dataclass
class ScheduleEntry:
   
    time_unit: int
    mechanic_id: int 
    task: Optional[Task] = None
    is_break: bool = False

    def display(self, col_w: int = 20) -> str:
        if self.is_break:
            return f"{'[BREAK]':<{col_w}}"
        if self.task:
            tag = "*" if self.task.is_spawn else " "
            s = f"[{tag}{self.task.task_id}({self.task.car_inst}){tag}]"
            return f"{s:<{col_w}}"
        return f"{'[----]':<{col_w}}"


@dataclass
class MechanicState:
    """Runtime fatigue tracker per mechanic."""

    label: str  
    consecutive: int = 0
    total_tasks: int = 0
    total_breaks: int = 0

class InputParser:

    _RE_COMMENT = re.compile(r"#.*$")
    _RE_CONFIG = re.compile(r"^(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?$")
    _RE_CAR = re.compile(r"^CAR\s+(\S+)\s+(\d+)$", re.IGNORECASE)
    _RE_TASK = re.compile(r"^TASK\s+(\S+)(?:\s+->\s+(.+))?$", re.IGNORECASE)
    _RE_EDGE = re.compile(r"(\S+):([0-9]*\.?[0-9]+)")

    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self):
        lines = self._load()
        return self._parse_lines(lines)

    def _load(self):
        p = Path(self.filepath)
        if not p.exists():
            self._die(f"File not found: '{self.filepath}'")
        cleaned = []
        with p.open("r", encoding="utf-8") as fh:
            for i, raw in enumerate(fh, 1):
                line = self._RE_COMMENT.sub("", raw).strip()
                if line:
                    cleaned.append((i, line))
        return cleaned

    def _parse_lines(self, lines):
        if not lines:
            self._die("Input file is empty.")

        lineno, text = lines[0]
        m = self._RE_CONFIG.match(text)
        if not m:
            self._die(f"Line {lineno}: expected 'N  M  k  [seed]', got: {text!r}")
        N = int(m.group(1))
        M = int(m.group(2))
        k = int(m.group(3))
        seed = int(m.group(4)) if m.group(4) else None
        for name, val in (
            ("N (car types)", N),
            ("M (mechanics)", M),
            ("k (fatigue)", k),
        ):
            if val < 1:
                self._die(f"Line {lineno}: {name} must be >= 1, got {val}")

        config = {"N": N, "M": M, "k": k, "seed": seed}

        car_dags = []
        rest = lines[1:]
        car_count = 0
        while rest:
            lineno, text = rest[0]

            m = self._RE_CAR.match(text)
            if not m:
                self._die(
                    f"Line {lineno}: expected 'CAR <TypeName> <instances>', "
                    f"got: {text!r}"
                )

            type_name = m.group(1)
            num_instances = int(m.group(2))
            if num_instances < 1:
                self._die(
                    f"Line {lineno}: number of instances for CAR '{type_name}' "
                    f"must be >= 1"
                )
            rest = rest[1:]
            car_count += 1

            dag = CarTypeDAG(type_name=type_name)
            task_seen = 0

            while rest:
                ln2, txt2 = rest[0]
                if self._RE_CAR.match(txt2):
                    break  
                m2 = self._RE_TASK.match(txt2)
                if not m2:
                    self._die(
                        f"Line {ln2}: expected 'TASK <id> [-> <child>:<prob> ...]', "
                        f"got: {txt2!r}"
                    )
                task_id = m2.group(1)
                edge_part = m2.group(2)  

                dag.add_task(task_id)
                task_seen += 1

                if edge_part:
                    for em in self._RE_EDGE.finditer(edge_part):
                        child_id = em.group(1)
                        prob = float(em.group(2))
                        if not 0.0 <= prob <= 1.0:
                            self._die(
                                f"Line {ln2}: probability {prob} for edge "
                                f"{task_id}->{child_id} must be in [0.0, 1.0]"
                            )
                        dag.add_edge(task_id, child_id, prob)

                rest = rest[1:]

            if task_seen == 0:
                self._die(f"CAR '{type_name}' has no TASK lines.")

            car_dags.append((type_name, num_instances, dag))

        if car_count != N:
            self._die(
                f"Config says N={N} car types, but found {car_count} CAR block(s)."
            )

        return config, car_dags

    @staticmethod
    def _die(msg: str):
        print(f"\n[INPUT ERROR] {msg}\n", file=sys.stderr)
        sys.exit(1)

def build_car_instances(car_dags: list) -> list:

    instances = []
    counter = 1

    for type_name, num_instances, dag in car_dags:
        for _ in range(num_instances):
            label = f"C{counter}"
            counter += 1
            dag_copy = CarTypeDAG(type_name=type_name)
            for tid in dag.tasks:
                dag_copy.add_task(tid)
            for e in dag.edges:
                dag_copy.add_edge(e.parent_id, e.child_id, e.probability)

            instances.append((label, dag_copy))

    return instances

class GarageScheduler:

    def __init__(self, M: int, k: int, rng: random.Random, verbose: bool = False):
        self.M = M
        self.k = k
        self.rng = rng
        self.verbose = verbose

        self.mech_labels = [f"M{i+1}" for i in range(M)]
        self.mech_states = [MechanicState(label=f"M{i+1}") for i in range(M)]

        self.grid: list[list[ScheduleEntry]] = [[] for _ in range(M)]

        self.current_time = 0
        self.log: list[str] = []
        self.spawned_tasks: list[Task] = []

    def build_initial_schedule(self, instances: list):

        self._log("=" * 70)
        self._log("PHASE 1 — BUILDING INITIAL OPTIMAL SCHEDULE")
        self._log("=" * 70)

        queue: deque = deque()
        for car_label, dag in instances:
            for tid in dag.topological_order():
                t = Task(task_id=tid, car_inst=car_label)
                queue.append((t, dag))

        self._log(f"Total initial tasks to schedule : {len(queue)}")
        self._assign(queue)

    def _assign(self, queue: deque):

        m_cursor = 0
        while queue:
            task, dag = queue.popleft()
            m = m_cursor % self.M
            m_cursor += 1

            ms = self.mech_states[m]
            row = self.grid[m]
            lbl = self.mech_labels[m]

            if ms.consecutive >= self.k:
                t_brk = len(row)
                row.append(ScheduleEntry(time_unit=t_brk, mechanic_id=m, is_break=True))
                ms.consecutive = 0
                ms.total_breaks += 1
                self._log(
                    f"  {lbl} -> t={t_brk:>3}: [BREAK] "
                    f"(after {self.k} consecutive tasks)"
                )

            t_slot = len(row)
            row.append(ScheduleEntry(time_unit=t_slot, mechanic_id=m, task=task))
            ms.consecutive += 1
            ms.total_tasks += 1
            spawn_tag = " [SPAWNED]" if task.is_spawn else ""
            self._log(
                f"  {lbl} -> t={t_slot:>3}: "
                f"{task.task_id}({task.car_inst}){spawn_tag}"
            )


    def run(self, instances: list):

        dag_map: dict = {lbl: dag for lbl, dag in instances}
        max_t = self._max_time()

        self._log(f"\n{'=' * 70}")
        self._log("PHASE 2 — PROBABILISTIC SIMULATION")
        self._log(f"{'=' * 70}")

        while self.current_time < max_t:
            new_tasks = self._tick(dag_map)
            if new_tasks:
                self.spawned_tasks.extend(new_tasks)
                spawn_queue: deque = deque()
                for st in new_tasks:
                    dag = dag_map.get(st.car_inst)
                    if dag:
                        spawn_queue.append((st, dag))
                self._log(
                    f"\n  SCHEDULE UPDATE: inserting " f"{len(new_tasks)} sub-task(s)"
                )
                self._assign(spawn_queue)
                max_t = self._max_time() 

    def _tick(self, dag_map: dict) -> list:
        t = self.current_time
        new_tasks = []
        self._log(f"\n--- t={t} ---")

        for m in range(self.M):
            lbl = self.mech_labels[m]
            row = self.grid[m]

            if t >= len(row):
                if self.verbose:
                    self._log(f"  {lbl}: idle (no slot at t={t})")
                continue

            entry = row[t]
            if entry.is_break:
                self._log(f"  {lbl}: [BREAK]")
                continue
            if entry.task is None:
                if self.verbose:
                    self._log(f"  {lbl}: idle")
                continue

            task = entry.task
            self._log(f"  {lbl}: done  {task.task_id}({task.car_inst})")

            dag = dag_map.get(task.car_inst)
            if dag is None:
                continue

            for edge in dag.children.get(task.task_id, []):
                roll = self.rng.random()
                spawned = roll > edge.probability
                child_id = edge.child_id
                if spawned:
                    st = Task(task_id=child_id, car_inst=task.car_inst, is_spawn=True)
                    new_tasks.append(st)
                    self._log(
                        f"       SPAWN {child_id}({task.car_inst})  "
                        f"prob={edge.probability:.2f}  roll={roll:.2f}  FIRES"
                    )
                else:
                    self._log(
                        f"       no spawn {child_id}  "
                        f"prob={edge.probability:.2f}  roll={roll:.2f}"
                    )

        self.current_time += 1
        return new_tasks


    def display_schedule(self, title: str = "SCHEDULE"):
        max_t = self._max_time()
        col_w = 22
        t_col = 5

        # Header
        print(f"\n{'=' * 70}")
        print(title)
        print(f"{'=' * 70}")
        print(f"  Legend:")
        print(f"    [ A1(C2) ] = planned task   A1 for car C2")
        print(f"    [*A11(C2)*]= spawned sub-task")
        print(f"    [BREAK]    = mandatory rest")
        print(f"    [----]     = mechanic idle\n")

        sep = "-" * (t_col + 3 + col_w * self.M)
        hdr = f"{'t':>{t_col}} | "
        hdr += "".join(f"{self.mech_labels[m]:<{col_w}}" for m in range(self.M))
        print(hdr)
        print(sep)

        for t in range(max_t):
            row_str = f"{t:>{t_col}} | "
            for m in range(self.M):
                r = self.grid[m]
                entry = r[t] if t < len(r) else None
                if entry is None:
                    row_str += f"{'[----]':<{col_w}}"
                else:
                    row_str += entry.display(col_w)
            print(row_str)

    def display_summary(self, instances: list):
        max_t = self._max_time()
        total_spawned = len(self.spawned_tasks)
        total_tasks = sum(ms.total_tasks for ms in self.mech_states)
        total_breaks = sum(ms.total_breaks for ms in self.mech_states)

        print(f"\n{'=' * 70}")
        print("SUMMARY")
        print(f"{'=' * 70}")
        print(f"  Mechanics (M)        : {self.M}  " f"({', '.join(self.mech_labels)})")
        print(f"  Fatigue limit (k)    : {self.k}")
        print(
            f"  Cars serviced        : {len(instances)}  "
            f"({', '.join(lbl for lbl,_ in instances)})"
        )
        print(f"  Total time units     : {max_t}")
        print(f"  Total tasks completed: {total_tasks}")
        print(f"  Sub-tasks spawned    : {total_spawned}")
        print(f"  Total breaks taken   : {total_breaks}")
        print()
        print(
            f"  {'Mechanic':<10} {'Tasks':>6}  {'Breaks':>6}  " f"{'Utilisation':>12}"
        )
        print(f"  {'-'*10} {'-'*6}  {'-'*6}  {'-'*12}")
        for m in range(self.M):
            ms = self.mech_states[m]
            util = (ms.total_tasks / max_t * 100) if max_t else 0.0
            print(
                f"  {ms.label:<10} {ms.total_tasks:>6}  "
                f"{ms.total_breaks:>6}  {util:>11.1f}%"
            )

        if total_spawned:
            print(f"\n  Spawned sub-tasks:")
            for t in self.spawned_tasks:
                print(f"    {t.task_id}  for car {t.car_inst}")


    def _max_time(self) -> int:
        return max((len(row) for row in self.grid), default=0)

    def _log(self, msg: str):
        self.log.append(msg)
        print(msg)


def main():
    ap = argparse.ArgumentParser(
        prog="garage_scheduler.py",
        description="Garage Scheduler — input from structured .txt file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--input",
        "-i",
        required=True,
        metavar="FILE",
        help="Path to input file (e.g. input.txt)",
    )
    ap.add_argument(
        "--seed",
        "-s",
        type=int,
        default=None,
        metavar="INT",
        help="Override the random seed from the input file",
    )
    ap.add_argument(
        "--verbose", "-v", action="store_true", help="Log idle slots during simulation"
    )
    ap.add_argument(
        "--output",
        "-o",
        default="output.txt",
        metavar="FILE",
        help="Path to output file (default: output.txt)",
    )
    args = ap.parse_args()

    output_file = open(args.output, "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = output_file

    try:
        print(f"\nReading: {args.input}")
        parser = InputParser(args.input)
        config, car_dags = parser.parse()

        N = config["N"]
        M = config["M"]
        k = config["k"]
        seed = args.seed if args.seed is not None else config["seed"]

        print("=" * 70)
        print("GARAGE SCHEDULER")
        print("=" * 70)
        print(f"  Car types (N)     : {N}")
        print(
            f"  Mechanics (M)     : {M}  " f"({', '.join(f'M{i+1}' for i in range(M))})"
        )
        print(f"  Fatigue limit (k) : {k}")
        print(
            f"  Random seed       : "
            f"{seed if seed is not None else 'non-deterministic'}"
        )

        print("\nCar Type DAGs (adjacency list):")
        total_instances = 0
        for type_name, num_inst, dag in car_dags:
            print(dag.display())
            print(f"    Instances scheduled: {num_inst}")
            total_instances += num_inst

        instances = build_car_instances(car_dags)
        print(f"\nCar instances ({total_instances} total):")
        for lbl, dag in instances:
            print(
                f"  {lbl} -> {dag.type_name}  "
                f"[tasks: {', '.join(dag.topological_order())}]"
            )

        rng = random.Random(seed)
        scheduler = GarageScheduler(M=M, k=k, rng=rng, verbose=args.verbose)
        scheduler.build_initial_schedule(instances)
        scheduler.display_schedule(title="INITIAL SCHEDULE GRID")

        scheduler.run(instances)

        scheduler.display_schedule(title="FINAL SCHEDULE GRID  (* = spawned sub-task)")
        scheduler.display_summary(instances)

    finally:
        sys.stdout = original_stdout
        output_file.close()
        print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
