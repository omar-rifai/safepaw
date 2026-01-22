import backend.core.optimization as mdl
import pulp
from backend.core.utils.data_utils import package_results, define_xarray
from backend.core.optimization import declare_constraints, set_obj_fn


def run_driver(params_system):
    
    try:
    # Line below useful for the Burdett's data, in order to get \sum_{u} \underline{q}_{g,u} = \sum_{u} \overline{q}_{g,u} = 1
        params_system["Under_q_gu"], params_system["Over_q_gu"] = mdl.change_Under_Over(params_system["G"], params_system["U"], params_system["Under_q_gu"], params_system["Over_q_gu"])
    except Exception as e:
        print(e, "No Under_q_gu and Over_q_gu modification needed")

    # Define K2 and A2 (usefull sets for creating the variables)
   
    K2 = mdl.defineK2(params_system["K_g"])
    A2 = mdl.defineA2(params_system["A_gk"])
    
    # Create the LP, wich is a maximization problem
   
    LP = pulp.LpProblem('Regional Case Mix', pulp.LpMaximize)
    

    P = pulp.LpVariable.dicts("P", (params_system["G"], K2, params_system["R"], A2, params_system["H"]), 0, None)
    P_gkr = pulp.LpVariable.dicts("P_gkr", (params_system["G"], K2, params_system["R"]), 0, None)
    P_gk = pulp.LpVariable.dicts("P_gk", (params_system["G"], K2), 0, None)
    Q = pulp.LpVariable.dicts("Q", (params_system["G"], K2, params_system["R"], A2, params_system["H"]), 0, None)
    
    Delta_plus = pulp.LpVariable.dicts("Delta_plus", (params_system["H"], params_system["L"]), 0, None)
    Delta_moins = pulp.LpVariable.dicts("Delta_moins", (params_system["H"], params_system["L"]), 0, None)
    
    z_hl_plus = pulp.LpVariable.dicts("z_hl_plus", (params_system["H"], params_system["L"]), cat=pulp.LpInteger, lowBound = 0)
    z_hl_moins = pulp.LpVariable.dicts("z_hl_moins", (params_system["H"], params_system["L"]), cat=pulp.LpInteger, lowBound = 0)
    
    # Define the objective function
    set_obj_fn(LP, P_gk, P, Delta_plus, Delta_moins, params_system)
    
    print("Declaring Constraints...")
 
    # Set the constraints
    declare_constraints(LP, P_gk, params_system["G"], params_system["K_g"], P_gkr, params_system["R"], P, params_system["A_gk"], params_system["H"], Q, Delta_plus,
                        Delta_moins, params_system["L"], z_hl_plus, z_hl_moins, params_system["d_gr"], params_system["Under_q_g"], params_system["Over_q_g"],
                        params_system["U"], params_system["I_gu"], params_system["Under_q_gu"], params_system["Over_q_gu"], params_system["O_gk"], params_system["J_h"], params_system["N_gka_1"], params_system["N_gka_2"],
                        params_system["p_transf"], params_system["t_gkal"], params_system["m_hl"], params_system["D"], params_system["delta_l"], params_system["b_hl_in"], params_system["b_hl_out"])
    # Solve the model
    
    print("Starting solver...")
    

    LP.solve(pulp.HiGHS_CMD(msg=1)) #options=["--tmlim", "10", "--nointopt", "--nopresol"])))
    
    dict_results = package_results(P_gk, P_gkr, P, Q, Delta_plus, Delta_moins,z_hl_plus, z_hl_moins)
    
    dict_xarray_results = define_xarray(params_system, dict_results)

    status =  pulp.LpStatus[LP.status]
    objective = pulp.value(LP.objective)

    return status, objective, dict_xarray_results
    



if __name__ == "__main__":

    from backend.core.utils.data_utils import read_configs_file
    import json

    input_file = read_configs_file("paths", "sample_input_file")

    with open(input_file) as file:
        params_system = json.load(file)

    run_driver(params_system)
