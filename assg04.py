import sys
from z3 import *
import math
def parse_input(filename):
    K = None
    prices = []
    vehicles = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("%"):
                continue

            parts = line.split()

            if parts[0] == "K":
                K = int(parts[1])

            elif parts[0] == "P":
                prices = list(map(int, parts[1:]))

            elif parts[0] == "V":
                vid = int(parts[1])
                arrival = int(parts[2])
                departure = int(parts[3])
                charge = int(parts[4])
                vehicles.append((vid, arrival, departure, charge))

    return K, prices, vehicles


def solve_charging_schedule(filename):

    K, prices, vehicles = parse_input(filename)

    n = len(vehicles)
    opt = Optimize()

    port = {}
    start = {}
    end = {}

    for i in range(n):
        vid, arrival, departure, charge = vehicles[i]

        port[i] = Int(f"port_{vid}")
        start[i] = Int(f"start_{vid}")
        end[i] = Int(f"end_{vid}")

        opt.add(port[i] >= 1, port[i] <= K)

        charging_time = Sum([
            If(port[i] == k,
               math.ceil(charge / k),
               0)
            for k in range(1, K + 1)
        ])

        opt.add(end[i] == start[i] + charging_time)
        opt.add(start[i] >= arrival)
        opt.add(end[i] <= departure)

    for i in range(n):
        for j in range(i + 1, n):
            opt.add(
                Or(
                    port[i] != port[j],
                    end[i] <= start[j],
                    end[j] <= start[i]
                )
            )

    total_cost = Sum([
        Sum([
            If(port[i] == k,
               prices[k-1] * math.ceil(vehicles[i][3] / k),
               0)
            for k in range(1, K + 1)
        ])
        for i in range(n)
    ])

    opt.minimize(total_cost)

    if opt.check() == sat:
        model = opt.model()

        print("Optimal Schedule Found")
        print("Total Cost:", model.evaluate(total_cost))

        for i in range(n):
            vid = vehicles[i][0]
            print(f"\nVehicle {vid}")
            print("  Port :", model[port[i]])
            print("  Start:", model[start[i]])
            print("  End  :", model[end[i]])
    else:
        print("No feasible schedule found")

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python schedule.py <input-file>")
        sys.exit(1)

    filename = sys.argv[1]
    solve_charging_schedule(filename)