def run_legacy_reader(data_file: str) -> dict:
    from backend.core.utils.legacy_data_utils import readCompleteDataFile

    G, K_g, R, A_gk, H, L, c_gk, alpha, w_rh, D, d_gr, t_gkal, m_hl,\
    Under_q_g, Over_q_g, U, I_gu, Under_q_gu, Over_q_gu, O_gk, J_h, p_transf, b_hl_in, b_hl_out,\
    delta_l, N_gka_1, N_gka_2 = readCompleteDataFile(data_file)

    params_system = {
        "G": G, # list of patient groups
        "R": R, # list of regions
        "H": H, # list of facilities
        "L": L, # list of resource types
        "A_gk": A_gk, #A_gk: size of activties for pathway k of group g (all group have the same number of pathways?)
        "t_gkal": t_gkal, #t_gkal: consumption of resource l required to perform care activity a of pathway k of group g
        "m_hl": m_hl, #m_hl: total capacity of resource type l in healthcare facility h
        "I_gu": I_gu, #I_gu: pathways available for group g that meet quality level u
        "O_gk": O_gk, #O_gk: set of facilities that can treat group g following pathway k
        "J_h": J_h,  #J_h: set of facilities which can receive patients from facility h
        "delta_l": delta_l, #delta_l: transfer unit for resource of type l
        "N_gka_1": N_gka_1, #N_gka_1/2: next activity to be considered for transfer after activity a of pathway k of group g
        "N_gka_2": N_gka_2,

        # preference params
        "alpha": alpha, #alpha: care quality vs patients satisfaction
        "D": D, #d: target patients treated
        "p_transf": p_transf, # max perc of patients that can be transfered
        
    
        "c_gk": c_gk, #c_gk: benefit score of assigning patients from group g to pathway k
        "K_g": K_g, #K_g: prefered care pathway ID for group g
        "w_rh": w_rh,  #preference score of patients from region r for facility h
        "d_gr": d_gr, #d_gr: minimum treatment threshold of patient group g from region r
        "Under_q_g": Under_q_g, #under_q_g: min proportion of patients of group g to be treated
        "Over_q_g": Over_q_g, #over_q_g: max proportin of patients of group g to be treated
        "Under_q_gu": Under_q_gu, #under_q_g_u: min proportion of patients of group g to be treated with quality level u 
        "Over_q_gu": Over_q_gu, #over_q_g_u: max proportin of patients of group g to be treated with quality level u
        "U": U, #U(g): quality level required for care pathways of group g 
        "b_hl_in": b_hl_in, #b_hl_ini: max proportions of resources of type l transferable to facility h
        "b_hl_out": b_hl_out #b_hl_ini: max proportions of resources of type l transferable out of facility h
    }
    return params_system



if __name__ == "__main__":
    from pathlib import Path
    import json
    path_in = Path("backend/data/legacy/legacy_format_Burdett_v0.txt")
    path_out = path_in.with_suffix(".json")
    
    print(f"Importing legacy .txt data from: {path_in}... \n")
   
    params_system = run_legacy_reader(path_in)
    with open(path_out, "w") as fp:
        json.dump(params_system, fp)

    print(f"JSON saved to: {path_out}. \n")
