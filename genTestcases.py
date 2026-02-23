import sys
import os
import random


def generate_test_case(
        filename,
        K,
        num_vehicles,
        arr_min, arr_max,
        dep_gap_min, dep_gap_max,
        charge_min, charge_max):
    prices = sorted([random.randint(5, 40) for _ in range(K)])
    vehicles = []
    for vid in range(1, num_vehicles + 1):
        arrival = random.randint(arr_min, arr_max)
        gap = random.randint(dep_gap_min, dep_gap_max)
        departure = arrival + gap
        charge_time = random.randint(charge_min, charge_max)
        vehicles.append((vid, arrival, departure, charge_time))

    with open(filename, "w") as f:
        f.write("% number of ports- K\n")
        f.write(f"K {K}\n\n")
        f.write("% Price for ports per time unit\n")
        f.write("P " + " ".join(map(str, prices)) + "\n\n")
        f.write("% vehicle requests: id arrival-time departure-time charge-time\n")
        for v in vehicles:
            f.write(f"V {v[0]} {v[1]} {v[2]} {v[3]}\n")

def main():
    if len(sys.argv) != 10:
        print(
            "Usage:\n"
            "python generate_tests.py "
            "<num_tests> <num_ports> <num_vehicles> "
            "<arr_min> <arr_max> "
            "<dep_gap_min> <dep_gap_max> "
            "<charge_min> <charge_max>"
        )
        sys.exit(1)
    num_tests = int(sys.argv[1])
    K = int(sys.argv[2])
    num_vehicles = int(sys.argv[3])
    arr_min = int(sys.argv[4])
    arr_max = int(sys.argv[5])
    dep_gap_min = int(sys.argv[6])
    dep_gap_max = int(sys.argv[7])
    charge_min = int(sys.argv[8])
    charge_max = int(sys.argv[9])
    folder_name = "inputs"
    os.makedirs(folder_name, exist_ok=True)
    for i in range(1, num_tests + 1):
        filename = os.path.join(
            folder_name,
            f"input{i:02d}.txt"
        )
        generate_test_case(
            filename,
            K,
            num_vehicles,
            arr_min, arr_max,
            dep_gap_min, dep_gap_max,
            charge_min, charge_max
        )
    print(f"Generated {num_tests} test cases inside '{folder_name}' folder.")
if __name__ == "__main__":
    main()