import sys
import copy

def read_input(filename):
    assignments={}
    N=K=None
    with open(filename,"r") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("%"):
                continue
            parts=line.split()
            if parts[0]=='N':
                N=int(parts[1])
            elif parts[0]=='K':
                K=int(parts[1])
            elif parts[0]=='A':
                aid=int(parts[1])
                prompts=int(parts[2])
                deps=[]
                for d in parts[3:]:
                    if d=='0':
                        break
                    deps.append(int(d))
                assignments[aid]={
                    "prompts":prompts,
                    "deps":deps
                }
    return N,K,assignments

def check(aid,assignments,completed):
    for d in assignments[aid]['deps']:
        if d not in completed:
            return False
    return True

def back(day,max_day,N,K,assignments,completed,schedule,all_schedules):
    if len(completed)==len(assignments):
        all_schedules.append(copy.deepcopy(schedule))
        return
    if day>max_day:
        return
    if day not in schedule:
        schedule[day]={}
        for s in range(N):
            schedule[day][s]=[]
    schedule[day]={s: [] for s in range(N)}
    prompt_left={s:K for s in range(N)}
    
    def assign(aid_list,idx):
        if idx==len(aid_list):
            back(day+1,max_day,N,K,assignments,completed,schedule,all_schedules)
            return
        aid=aid_list[idx]
        if aid in completed or not check(aid,assignments,completed):
            assign(aid_list,idx+1)
            return
        assign(aid_list,idx+1)
        progress=False
        for s in range(N):
            need=assignments[aid]["prompts"]
            if prompt_left[s]>=need:
                prompt_left[s]-=need
                completed.add(aid)
                schedule[day][s].append(aid)
                assign(aid_list,idx+1)
                schedule[day][s].pop()
                completed.remove(aid)
                prompt_left[s]+=need
                
    
    assign(list(assignments.keys()),0)
    del schedule[day]
    
if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: python assgn01_final.py <input-file> <days>")
        sys.exit(1)
    filename=sys.argv[1]
    max_day=int(sys.argv[2])
    N,K,assignments=read_input(filename)
    all_schedules=[]
    back(1,max_day,N,K,assignments,set(),{},all_schedules)
    print(f"\nTotal valid schedules: {len(all_schedules)}\n")
    
    for i,sch in enumerate(all_schedules,1):
        print(f"Schedule{i}: ")
        for day in sch:
            print(f"Day {day}:")
            for s in sch[day]:
                print(f" Student {s}: {sch[day][s]}")
        print('-'*40)