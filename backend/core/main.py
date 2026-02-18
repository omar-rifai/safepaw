import pulp
from backend.core.optimization import declare_constraints, set_obj_fn
from backend.core.utils.data_utils import package_results
import typer
from typing import Any
from pydantic import BaseModel
app = typer.Typer()


class OptVars(BaseModel):
    P : Any
    P_gk: Any
    P_gkr: Any
    Q: Any
    Delta_plus: Any
    Delta_moins:Any
    z_hl_plus: Any
    z_hl_moins: Any

def run_driver(params_system, mode="default"):

    LP = pulp.LpProblem('regional_case_mix', pulp.LpMaximize)

    P = {g: {k: {r: {a: {h: pulp.LpVariable(f"P_{g}_{k}_{r}_{a}_{h}", lowBound=0)
                         for h in params_system["H"]}
                         for a in params_system["A_idx"][g][k]}
                         for r in params_system["R"]}
                         for k in params_system["K_idx"][g]}
                         for g in params_system["G"]}

    P_gkr = {g: {k: {r: pulp.LpVariable(f"P_gkr_{g}_{k}_{r}", lowBound=0)
                     for r in params_system["R"]} 
                     for k in params_system["K_idx"][g]}
                     for g in params_system["G"]}

    P_gk = {g: {k: pulp.LpVariable(f"P_gk_{g}_{k}", lowBound=0)
                for k in params_system["K_idx"][g]}
                for g in params_system["G"]}

    Q = {g: {k: {r: {a: {h: pulp.LpVariable(f"Q_{g}_{k}_{r}_{a}_{h}", lowBound=0)
                         for h in params_system["H"]}
                         for a in params_system["A_idx"][g][k]}
                         for r in params_system["R"]}
                         for k in params_system["K_idx"][g]}
                         for g in params_system["G"]}

    Delta_plus = {h: {l: pulp.LpVariable(f"Delta_plus_{h}_{l}", lowBound=0)
                      for l in params_system["L"]}
                      for h in params_system["H"]}

    Delta_moins = {h: {l: pulp.LpVariable(f"Delta_moins_{h}_{l}", lowBound=0)
                       for l in params_system["L"]}
                       for h in params_system["H"]}

    z_hl_plus = {h: {l: pulp.LpVariable(f"z_hl_plus_{h}_{l}", cat=pulp.LpInteger, lowBound=0)
                     for l in params_system["L"]}
                     for h in params_system["H"]}

    z_hl_moins = {h: {l: pulp.LpVariable(f"z_hl_moins_{h}_{l}", cat=pulp.LpInteger, lowBound=0) 
                      for l in params_system["L"]}
                      for h in params_system["H"]}


    vars_system = OptVars(P=P,P_gkr=P_gkr,P_gk=P_gk,Q=Q,Delta_plus=Delta_plus, Delta_moins=Delta_moins, z_hl_plus=z_hl_plus, z_hl_moins=z_hl_moins)

    set_obj_fn(LP, P_gk, P, Delta_plus, Delta_moins, params_system, mode)
    print("Declaring Constraints...")
    declare_constraints(LP, vars_system, params_system, mode)
    print("Starting solver...")

    LP.solve(pulp.HiGHS(msg=1))
    dict_results = package_results(vars_system, params_system)
    status =  pulp.LpStatus[LP.status]
    objective = pulp.value(LP.objective)

    return status, objective, dict_results
    


def main():
    import sys
    import json
    import os

    
    path = sys.argv[1]
    with open(path) as fp:
        params_system = json.load(fp)
    _, _, dict_results = run_driver(params_system)
    
    os.makedirs("./backend/data/temp", exist_ok=True)
    with open("./backend/data/temp/outputs.json", "w+") as fp:
        json.dump({k: (v.to_dict(orient="records")) for k,v in dict_results.items()}, fp)
    

if __name__ == "__main__":
    main()



    
