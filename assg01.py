import sys

m=sys.argv[1]
#print("m = ",m)
assgn=[]


with open("sample.txt",'r') as f:
    for line in f:
        if line[0]=='%':
            continue
        if line[0]=='K':
            k=line.split()[1]
        if line[0]=='N':
            n=line.split()[1]
        if line[0]=='A':
            new_assgn=line.split()
            new_assgn=new_assgn[2:-1]
            assgn.append([new_assgn[0],tuple(new_assgn[1:])])

# print("k = ",k)
# print("n = ",n)
print("Assgns = ",assgn)

assgn_no=[i for i in range(1,len(assgn)+1)]
indegree=[len(a[1]) for a in assgn]
# print("indegrees = ",indegree)
def permutation(nums,l,r,visited):
    if l==r:
        visited.add(tuple(nums))
    else:
        for i in range(l,r+1):
            nums[i],nums[l]=nums[l],nums[i]
            permutation(nums,l+1,r,visited)
            nums[i],nums[l]=nums[l],nums[i]

def is_valid(schedule):
    i=-1
    for assignment in schedule:
        i+=1
        if len(assgn[assignment-1][1])==0:
            continue
        for dep in assgn[assignment-1][1]:
            if (int(dep)) not in schedule[:i]:
                return False
    return True


def is_prompt_valid(schedule):
    days=0
    i=0
    while(1):
        prompts=[int(k) for _ in range(int(n))]
        days+=1
        check=1
        while(check):
            if i>=len(schedule):
                return(days)
            print(prompts)
            needed=int(assgn[schedule[i]-1][0])
            check=0
            for j in range(len(prompts)):
                if prompts[j]>=needed:
                    prompts[j]-=needed
                    i+=1
                    check=1
                    break
    return(days)


visited=set()
permutation(assgn_no,0,len(assgn_no)-1,visited)
for v in visited:
    if is_valid(v):
        print(v)
print(is_prompt_valid([1,7,2,4,5,6,8,3]))
