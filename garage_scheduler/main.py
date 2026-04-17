import sys, re, random, argparse, math
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: str
    car_inst: str
    is_spawn: bool = False


@dataclass
class Edge:
    parent_id: str
    child_id: str
    prob: float


@dataclass
class CarTypeDAG:
    type_name: str
    tasks: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    children: dict = field(default_factory=dict)

    def add_edge(self, p: str, c: str, prob: float):
        for t in (p, c):
            if t not in self.tasks:
                self.tasks[t] = Task(t, "?")
                self.children[t] = []
        e = Edge(p, c, prob)
        self.edges.append(e)
        self.children[p].append(e)

    def top_order(self):
        in_d = {t: sum(1 for e in self.edges if e.child_id == t) for t in self.tasks}
        q, ord_t = deque(t for t, d in in_d.items() if d == 0), []
        while q:
            t = q.popleft()
            ord_t.append(t)
            for e in self.children[t]:
                in_d[e.child_id] -= 1
                if in_d[e.child_id] == 0:
                    q.append(e.child_id)
        if len(ord_t) != len(self.tasks):
            raise ValueError(f"Cycle in {self.type_name}")
        return ord_t


@dataclass
class ScheduleEntry:
    time_unit: int
    mechanic_id: int
    task: Task = None
    is_break: bool = False

    def display(self, w=24):
        if self.is_break:
            return f"{'[BREAK]':<{w}}"
        if not self.task:
            return f"{'[----]':<{w}}"
        tg = "*" if self.task.is_spawn else " "
        return f"[{tg}{self.task.task_id}({self.task.car_inst}){tg}]".ljust(w)


class InputParser:
    def __init__(self, fp):
        self.fp = fp

    def parse(self):
        with open(self.fp, "r", encoding="utf-8") as f:
            ls = [(i, re.sub(r"#.*$", "", l).strip()) for i, l in enumerate(f, 1)]
        ls = [(i, l) for i, l in ls if l]
        m = re.match(r"^(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?$", ls[0][1])
        cfg = {
            "N": int(m[1]),
            "M": int(m[2]),
            "k": int(m[3]),
            "seed": int(m[4]) if m[4] else None,
        }
        dags, rest = [], ls[1:]
        while rest:
            m = re.match(r"^CAR\s+(\S+)\s+(\d+)$", rest[0][1], re.I)
            t_name, n_inst = m[1], int(m[2])
            dag, rest = CarTypeDAG(t_name), rest[1:]
            while rest and not re.match(r"^CAR", rest[0][1], re.I):
                m2 = re.match(r"^TASK\s+(\S+)(?:\s+->\s+(.+))?$", rest[0][1], re.I)
                tid, edges = m2[1], m2[2]
                dag.tasks.setdefault(tid, Task(tid, "?"))
                dag.children.setdefault(tid, [])
                if edges:
                    for c, p in re.findall(r"(\S+):([0-9]*\.?[0-9]+)", edges):
                        dag.add_edge(tid, c, float(p))
                rest = rest[1:]
            dags.append((t_name, n_inst, dag))
        return cfg, dags


def build_cars(dags):
    insts, c = [], 1
    for name, n, dag in dags:
        for _ in range(n):
            copy = CarTypeDAG(name)
            copy.tasks, copy.children = {k: Task(k, "?") for k in dag.tasks}, {
                k: [] for k in dag.tasks
            }
            for e in dag.edges:
                copy.add_edge(e.parent_id, e.child_id, e.prob)
            insts.append((f"C{c}", copy))
            c += 1
    return insts


def _makespan(tasks, M, k):
    r, c = [0] * M, [0] * M
    for i, _ in enumerate(tasks):
        m = i % M
        if c[m] >= k:
            r[m] += 1
            c[m] = 0
        r[m] += 1
        c[m] += 1
    return max(r, default=0)

class SA:
    def __init__(self, M, k, rng, iters):
        self.M, self.k, self.rng, self.iters = M, k, rng, iters

    def optimise(self, insts):
        cur = [Task(t, l) for l, d in insts for t in d.top_order()]
        deps = {((l, e.parent_id), (l, e.child_id)) for l, d in insts for e in d.edges}
        best, bc, cc, T, n = (
            cur[:],
            _makespan(cur, self.M, self.k),
            _makespan(cur, self.M, self.k),
            100.0,
            len(cur),
        )
        for _ in range(self.iters):
            if n < 2:
                break
            i, j = self.rng.sample(range(n), 2)
            ak, bk, lo = (
                (cur[i].car_inst, cur[i].task_id),
                (cur[j].car_inst, cur[j].task_id),
                min(i, j),
            )
            if ((bk, ak) in deps and lo == i) or ((ak, bk) in deps and lo == j):
                continue
            cur[i], cur[j] = cur[j], cur[i]
            nc = _makespan(cur, self.M, self.k)
            if nc < cc or self.rng.random() < math.exp(-(nc - cc) / max(T, 1e-9)):
                cc = nc
                if nc < bc:
                    bc, best = nc, cur[:]
            else:
                cur[i], cur[j] = cur[j], cur[i]
            T *= 0.995
        return best


class MCTSNode:
    def __init__(self, t=None, p=None):
        self.task, self.p, self.c, self.v, self.cost = t, p, [], 0, 0.0

    def uct(self):
        return (
            float("inf")
            if not self.v
            else -(self.cost / self.v) + 1.414 * math.sqrt(math.log(self.p.v) / self.v)
        )


class MCTS:
    def __init__(self, M, k, rng, sims):
        self.M, self.k, self.rng, self.sims = M, k, rng, sims

    def recommend(self, base, dmaps):
        sp = [
            (Task(e.child_id, l, True), 1 - e.prob)
            for l, d in dmaps.items()
            for t in d.tasks
            for e in d.children.get(t, [])
            if 1 - e.prob > 0
        ]
        if not sp:
            return []
        root = MCTSNode()
        root.c = [MCTSNode(t, root) for t, _ in sp]
        for _ in range(self.sims):
            n = root
            while n.c:
                n = max(n.c, key=lambda x: x.uct())
            if n != root:
                n.c = [MCTSNode(t, n) for t, _ in sp]
            cost = _makespan(
                base + [t for t, p in sp if self.rng.random() < p], self.M, self.k
            )
            while n:
                n.v += 1
                n.cost += cost
                n = n.p
        r_nodes = sorted([c for c in root.c if c.v > 0], key=lambda x: x.cost / x.v)[:5]
        return [
            n.task for n in r_nodes if (n.cost / n.v) < _makespan(base, self.M, self.k)
        ]

class GarageScheduler:
    def __init__(self, M, k, rng):
        self.M, self.k, self.rng, self.t, self.spawned = M, k, rng, 0, []
        self.labels, self.states = [f"M{i+1}" for i in range(M)], [
            {"c": 0, "t": 0, "b": 0} for _ in range(M)
        ]
        self.grid = [[] for _ in range(M)]

    def _assign(self, q):
        mc = 0
        while q:
            t, _ = q.popleft()
            m = mc % self.M
            mc += 1
            ms, r = self.states[m], self.grid[m]
            if ms["c"] >= self.k:
                r.append(ScheduleEntry(len(r), m, is_break=True))
                ms["c"] = 0
                ms["b"] += 1
            r.append(ScheduleEntry(len(r), m, task=t))
            ms["c"] += 1
            ms["t"] += 1

    def build_initial(self, ord_t, insts):
        dmap = {l: d for l, d in insts}
        self._assign(deque((t, dmap[t.car_inst]) for t in ord_t if t.car_inst in dmap))

    def run(self, insts, pre):
        dmap = {l: d for l, d in insts}
        if pre:
            self._assign(
                deque((t, dmap[t.car_inst]) for t in pre if t.car_inst in dmap)
            )
        while self.t < max((len(r) for r in self.grid), default=0):
            new_t = []
            for m, r in enumerate(self.grid):
                if self.t >= len(r) or r[self.t].is_break or not r[self.t].task:
                    continue
                t = r[self.t].task
                dag = dmap.get(t.car_inst)
                if not dag:
                    continue
                for e in dag.children.get(t.task_id, []):
                    if self.rng.random() > e.prob:
                        new_t.append(Task(e.child_id, t.car_inst, True))
            self.t += 1
            if new_t:
                self.spawned.extend(new_t)
                self._assign(deque((st, dmap[st.car_inst]) for st in new_t))

    def show_sched(self, title):
        mt = max((len(r) for r in self.grid), default=0)
        print(
            f"\n{title}\n{'='*70}\nLegend: [ A1(C2) ]=planned  [*X(C1)*]=spawned  [BREAK]=rest  [----]=idle\n"
        )
        print(
            f"{'t':>5} | "
            + "".join(f"{l:<24}" for l in self.labels)
            + "\n"
            + "-" * (8 + 24 * self.M)
        )
        for t in range(mt):
            print(
                f"{t:>5} | "
                + "".join(
                    (
                        self.grid[m][t].display()
                        if t < len(self.grid[m])
                        else "[----]".ljust(24)
                    )
                    for m in range(self.M)
                )
            )

    def show_sum(self, insts):
        mt = max((len(r) for r in self.grid), default=0)
        print(
            f"\nSUMMARY\n{'='*70}\nMechanics: {self.M} | Cars: {len(insts)} | Total Time units: {mt} | Tasks Spawned: {len(self.spawned)}"
        )
        print(
            f"\n{'Mechanic':<10} {'Tasks':>6}  {'Breaks':>6}  {'Utilisation':>12}\n"
            + "-" * 40
        )
        for m, s in zip(self.labels, self.states):
            print(
                f"{m:<10} {s['t']:>6}  {s['b']:>6}  {(s['t']/mt*100) if mt else 0:>11.1f}%"
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", required=True)
    ap.add_argument("-s", type=int)
    ap.add_argument("-v", action="store_true")
    ap.add_argument("-o", default="output.txt")
    ap.add_argument("--sa-iter", type=int, default=5000)
    ap.add_argument("--mcts-sims", type=int, default=200)
    ap.add_argument("--no-sa", action="store_true")
    ap.add_argument("--no-mcts", action="store_true")
    args = ap.parse_args()

    with open(args.o, "w", encoding="utf-8") as out:
        orig_std = sys.stdout
        sys.stdout = out
        try:
            cfg, dags = InputParser(args.i).parse()
            M, k, rng = (
                cfg["M"],
                cfg["k"],
                random.Random(args.s if args.s is not None else cfg["seed"]),
            )
            insts = build_cars(dags)
            ord_t = (
                [Task(t, l) for l, d in insts for t in d.top_order()]
                if args.no_sa
                else SA(M, k, rng, args.sa_iter).optimise(insts)
            )
            pre = (
                []
                if args.no_mcts
                else MCTS(M, k, rng, args.mcts_sims).recommend(
                    ord_t, {l: d for l, d in insts}
                )
            )

            sch = GarageScheduler(M, k, rng)
            sch.build_initial(ord_t, insts)
            sch.show_sched("INITIAL SCHEDULE (SA-Optimised)")
            sch.run(insts, pre)
            sch.show_sched("FINAL SCHEDULE (* = spawned)")
            sch.show_sum(insts)
        finally:
            sys.stdout = orig_std
            print(f"Processing complete. Results exported to: {args.o}")


if __name__ == "__main__":
    main()
