from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = model.NewBoolVar("x")

print("OR-Tools works")