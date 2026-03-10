import sys
import time
import subprocess
from ortools.sat.python import cp_model
import psutil

def read_input(filename):
    rooms = 0
    courses = []
    with open(filename) as f:
        for line in f:
            if line.startswith('%') or line.strip()=="":
                continue
            p=line.split()
            if p[0]=="M":
                rooms=int(p[1])
            elif p[0]=="C":
                cid=int(p[1])
                s=int(p[2])
                d=int(p[3])
                t=int(p[4])
                courses.append((cid,s,d,t))
    return rooms,courses

def write_cnf(file,clauses,num_vars):
    with open(file,"w") as f:
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str,c))+" 0\n")

def clause_stats(clauses):
    c2=0
    c3=0
    c4=0
    for c in clauses:
        l=len(c)
        if l==2:
            c2+=1
        elif l==3:
            c3+=1
        else:
            c4+=1
    return c2,c3,c4

def encoding1(rooms,courses):
    var_map={}
    clauses=[]
    vid=1
    for cid,s,d,t in courses:
        for r in range(rooms):
            for st in range(s,d-t+2):
                var_map[(cid,r,st)]=vid
                vid+=1
    num_vars=vid-1
    for cid,s,d,t in courses:
        v=[]
        for r in range(rooms):
            for st in range(s,d-t+2):
                v.append(var_map[(cid,r,st)])
        clauses.append(v)
        for i in range(len(v)):
            for j in range(i+1,len(v)):
                clauses.append([-v[i],-v[j]])
    for i in range(len(courses)):
        cid1,s1,d1,t1=courses[i]
        for j in range(i+1,len(courses)):
            cid2,s2,d2,t2=courses[j]
            for r in range(rooms):
                for st1 in range(s1,d1-t1+2):
                    for st2 in range(s2,d2-t2+2):
                        end1=st1+t1-1
                        end2=st2+t2-1
                        overlap=not(end1<st2 or end2<st1)
                        if overlap:
                            v1=var_map[(cid1,r,st1)]
                            v2=var_map[(cid2,r,st2)]
                            clauses.append([-v1,-v2])
    return num_vars,clauses

def encoding2(rooms,courses):
    x={}
    y={}
    clauses=[]
    vid=1
    for cid,s,d,t in courses:
        for r in range(rooms):
            x[(cid,r)]=vid
            vid+=1
        for st in range(s,d-t+2):
            y[(cid,st)]=vid
            vid+=1
    num_vars=vid-1
    for cid,s,d,t in courses:
        v=[x[(cid,r)] for r in range(rooms)]
        clauses.append(v)
        for i in range(len(v)):
            for j in range(i+1,len(v)):
                clauses.append([-v[i],-v[j]])
    for cid,s,d,t in courses:
        st=[y[(cid,k)] for k in range(s,d-t+2)]
        clauses.append(st)
        for i in range(len(st)):
            for j in range(i+1,len(st)):
                clauses.append([-st[i],-st[j]])
    for i in range(len(courses)):
        cid1,s1,d1,t1=courses[i]
        for j in range(i+1,len(courses)):
            cid2,s2,d2,t2=courses[j]
            for st1 in range(s1,d1-t1+2):
                for st2 in range(s2,d2-t2+2):
                    end1=st1+t1-1
                    end2=st2+t2-1
                    overlap=not(end1<st2 or end2<st1)
                    if overlap:
                        for r in range(rooms):
                            clauses.append([
                                -x[(cid1,r)],
                                -x[(cid2,r)],
                                -y[(cid1,st1)],
                                -y[(cid2,st2)]
                            ])
    return num_vars,clauses

def run_z3(file):
    start = time.time()
    subprocess.run(["./z3.exe", file], stdout=subprocess.PIPE)
    return time.time() - start

def build_model(rooms,courses):
    model=cp_model.CpModel()
    x={}
    y={}
    for cid,s,d,t in courses:
        for r in range(rooms):
            x[(cid,r)]=model.NewBoolVar(f"x_{cid}_{r}")
        for st in range(s,d-t+2):
            y[(cid,st)]=model.NewBoolVar(f"y_{cid}_{st}")
    for cid,s,d,t in courses:
        model.Add(sum(x[(cid,r)] for r in range(rooms))==1)
        model.Add(sum(y[(cid,st)] for st in range(s,d-t+2))==1)
    for i in range(len(courses)):
        cid1,s1,d1,t1=courses[i]
        for j in range(i+1,len(courses)):
            cid2,s2,d2,t2=courses[j]
            for st1 in range(s1,d1-t1+2):
                for st2 in range(s2,d2-t2+2):
                    end1=st1+t1-1
                    end2=st2+t2-1
                    overlap=not(end1<st2 or end2<st1)
                    if overlap:
                        for r in range(rooms):
                            model.Add(
                                x[(cid1,r)]
                                +x[(cid2,r)]
                                +y[(cid1,st1)]
                                +y[(cid2,st2)]
                                <=3
                            )
    return model

def run_ortools_default(rooms,courses):
    model=build_model(rooms,courses)
    solver=cp_model.CpSolver()
    start=time.time()
    solver.Solve(model)
    return time.time()-start

def run_ortools_sat(rooms,courses):
    model=build_model(rooms,courses)
    solver=cp_model.CpSolver()
    solver.parameters.search_branching=cp_model.FIXED_SEARCH
    start=time.time()
    solver.Solve(model)
    return time.time()-start

import random
def generate_random_case():
    rooms = random.randint(2,6)
    courses = []
    N = random.randint(3,8)
    for i in range(1,N+1):
        s = random.randint(1,20)
        dur = random.randint(1,5)
        d = s + random.randint(dur,10)
        courses.append((i,s,d,dur))
    return rooms, courses

def main():
    tests = 100
    results = {
        "z3_enc1": [],
        "z3_enc2": [],
        "cp_enc1": [],
        "cp_enc2": [],
        "sat_enc1": [],
        "sat_enc2": []
    }
    memory = {
        "z3_enc1": [],
        "z3_enc2": [],
        "cp_enc1": [],
        "cp_enc2": [],
        "sat_enc1": [],
        "sat_enc2": []
    }
    process = psutil.Process()
    for t in range(tests):
        rooms, courses = generate_random_case()
        v1, c1 = encoding1(rooms, courses)
        write_cnf("enc1.cnf", c1, v1)
        v2, c2 = encoding2(rooms, courses)
        write_cnf("enc2.cnf", c2, v2)
        mem_before = process.memory_info().rss
        time_taken = run_z3("enc1.cnf")
        mem_after = process.memory_info().rss
        results["z3_enc1"].append(time_taken)
        memory["z3_enc1"].append(mem_after - mem_before)
        mem_before = process.memory_info().rss
        time_taken = run_z3("enc2.cnf")
        mem_after = process.memory_info().rss
        results["z3_enc2"].append(time_taken)
        memory["z3_enc2"].append(mem_after - mem_before)
        mem_before = process.memory_info().rss
        time_taken = run_ortools_default(rooms, courses)
        mem_after = process.memory_info().rss
        results["cp_enc1"].append(time_taken)
        memory["cp_enc1"].append(mem_after - mem_before)
        mem_before = process.memory_info().rss
        time_taken = run_ortools_default(rooms, courses)
        mem_after = process.memory_info().rss
        results["cp_enc2"].append(time_taken)
        memory["cp_enc2"].append(mem_after - mem_before)
        mem_before = process.memory_info().rss
        time_taken = run_ortools_sat(rooms, courses)
        mem_after = process.memory_info().rss
        results["sat_enc1"].append(time_taken)
        memory["sat_enc1"].append(mem_after - mem_before)
        mem_before = process.memory_info().rss
        time_taken = run_ortools_sat(rooms, courses)
        mem_after = process.memory_info().rss
        results["sat_enc2"].append(time_taken)
        memory["sat_enc2"].append(mem_after - mem_before)

    print("\n====================================")
    print("Average Performance over", tests, "tests")
    print("====================================")
    for key in results:
        avg_time = sum(results[key]) / tests
        avg_mem = sum(memory[key]) / tests
        print(f"{key} -> Avg Time: {avg_time:.6f}s | Avg Memory: {avg_mem/1024:.2f} KB")

if __name__=="__main__":
    main()