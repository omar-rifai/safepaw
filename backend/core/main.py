import pulp
from backend.core.utils.data_utils import package_results, define_xarray
from backend.core.optimization import declare_constraints, set_obj_fn
import typer
from typing import Any
from pathlib import Path
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

    K_indices = list(range(max(params_system["K_g"]))) 
    A_indices = list(range(max(max(A_g) for A_g in params_system["A_gk"])))              
    LP = pulp.LpProblem('Regional Case Mix', pulp.LpMaximize)
    P = pulp.LpVariable.dicts("P", (params_system["G"], K_indices, params_system["R"], A_indices, params_system["H"]), 0, None)
    P_gkr = pulp.LpVariable.dicts("P_gkr", (params_system["G"], K_indices, params_system["R"]), 0, None)
    P_gk = pulp.LpVariable.dicts("P_gk", (params_system["G"], K_indices), 0, None)
    Q = pulp.LpVariable.dicts("Q", (params_system["G"], K_indices, params_system["R"], A_indices, params_system["H"]), 0, None)
    Delta_plus = pulp.LpVariable.dicts("Delta_plus", (params_system["H"], params_system["L"]), 0, None)
    Delta_moins = pulp.LpVariable.dicts("Delta_moins", (params_system["H"], params_system["L"]), 0, None)
    z_hl_plus = pulp.LpVariable.dicts("z_hl_plus", (params_system["H"], params_system["L"]), cat=pulp.LpInteger, lowBound = 0)
    z_hl_moins = pulp.LpVariable.dicts("z_hl_moins", (params_system["H"], params_system["L"]), cat=pulp.LpInteger, lowBound = 0)
    
    vars_system = OptVars(P=P,P_gkr=P_gkr,P_gk=P_gk,Q=Q,Delta_plus=Delta_plus, Delta_moins=Delta_moins, z_hl_plus=z_hl_plus, z_hl_moins=z_hl_moins)

    set_obj_fn(LP, P_gk, P, Delta_plus, Delta_moins, params_system, mode)
    print("Declaring Constraints...")
    declare_constraints(LP, vars_system, params_system, mode)
    print("Starting solver...")
    LP.solve(pulp.HiGHS_CMD(msg=1))
   
    dict_results = package_results(vars_system)
    dict_xarray_results = define_xarray(params_system, dict_results)
    status =  pulp.LpStatus[LP.status]
    objective = pulp.value(LP.objective)

    return status, objective, dict_xarray_results
    

@app.command()
def main(path: Path):
    import json
    with open(path) as fp:
        params_system = json.load(fp)
    run_driver(params_system)

if __name__ == "__main__":
    app(standalone_mode=False)



    
