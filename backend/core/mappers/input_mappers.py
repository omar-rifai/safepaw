from backend.core.data_models.input_models import Instance, SystemData

def validate_required_params(params, required_keys, msg):
    missing = [k for k in required_keys if k not in params]
    if missing:
        raise KeyError(f"Missing required parameters: {missing}. {msg}")


def create_json_from_patients(list_patients: list, params_system: dict) -> dict:
    """ Adds group ids  (G) to params_system"""
    params_system["G"] = list(dict.fromkeys(x.group_id for x in list_patients))
    return params_system


def reconstruct_L_from_resources(list_resources: list, params_system: dict) -> dict:
    """ Adds Resource types (L) to params_system"""
    params_system["L"] = [r.resource_id for r in list_resources]
    return params_system


def reconstruct_I_gu(list_pathways: list, params_system: dict) -> dict:
    """ Adds Set of pathways available to group g that fall under care quality level u to params_system"""
    validate_required_params(params_system, ["G"], "Construct patient groups first.")       
    I_gu = {}
    for g in params_system["G"]:
        I_g = {}
        for u in params_system["U_idx"][g]:
            I_g[u] = [k.pathway_id for k in [x for x in list_pathways if x.associated_group_id == g] if k.quality_level==u]
        I_gu[g] = I_g
    params_system["I_gu"] = I_gu
    return params_system


def reconstruct_c_gk(list_pathways: list, params_system: dict) -> dict:
    """ Adds c_gk ( Benefit score of assigning a patient from group g with the care pathway k) to params_system"""
    validate_required_params(params_system, ["G"], "Construct patient groups first.")
    c_gk = {}
    for g in params_system["G"]:
        c_gk[g] = {k.pathway_id: k.group_benefit for k in [k for k in list_pathways if k.associated_group_id == g]}
    params_system["c_gk"] = c_gk
    return params_system


def reconstruct_U_from_pathways(list_pathways: list, params_system: dict) -> dict:
    """ Adds U (Quality level u among the Ug quality levels of care pathways of group g) to params_system"""
    validate_required_params(params_system, ["G"], "Construct patient groups first.")
    U_idx = {}
    for g in params_system["G"]:
        U_idx[g] = [k.quality_level for k in list_pathways if k.associated_group_id == g]
    params_system["U_idx"] =  U_idx
    return params_system


def reconstruct_O_gk(list_facilities: list, params_system: dict) -> dict:
    """ Adds O_g,k (Set of healthcare facilities able to treat patient group g following pathway k) to params_system"""
    validate_required_params(params_system, ["K_idx", "G"], "Construct patient groups and pathways first")
    O = {}    
    for g in params_system["G"]:
        O_g = {}
        for k in params_system["K_idx"][g]:
            O_g[k] = [h.facility_id for h in list_facilities if k in h.available_pathways]
        O[g] = O_g
    params_system["O_gk"] = O
    return params_system


def reconstruct_J_h(list_facilities: list, params_system: dict) -> dict:
    """ Adds J_h (Set of healthcare facilities to which patients from facility h can be transferred) to params_system"""
    J = {}
    for h in list_facilities:
        J[h.facility_id] = [f for f in h.linked_facilities]
    params_system["J_h"] = J
    return params_system


def reconstruct_b_hl(list_facilities: list, params_system: dict) -> dict:
    """ Adds b_hl_in and b_hl_out (Maximum proportions of resource type l transferable to and from facility h) to params_system"""
    b_hl_in = {}
    b_hl_out = {}
    for h in list_facilities:
        b_hl_in[h.facility_id] = {}
        b_hl_out[h.facility_id] = {}
        for l in params_system["L"]:
            if l in h.resources_capacity.keys():
                b_hl_in[h.facility_id][l] = h.max_transferable_in[l]
                b_hl_out[h.facility_id][l] = h.max_transferable_out[l]
    params_system["b_hl_in"] = b_hl_in
    params_system["b_hl_out"] = b_hl_out
    return params_system


def reconstruct_t_gkal(list_activities: list, params_system: dict) -> dict:
    """Adds t_gkal (Consumption of resource l required to perform care activity a of pathway k of group g) to params_system"""
    validate_required_params(params_system, ["G", "K_idx"], "Construct patient groups and pathways first.")
    t = {g : {k: {} for k in params_system["K_idx"][g]} for g in params_system["G"]}  

    for a in list_activities:
        g, k =  a.associated_group, a.associated_pathway
        t[g][k][a.activity_id] = a.required_resources 
    
    params_system["t_gkal"] = t
    return params_system


def reconstruct_wrh(list_regions: list, params_system: dict) -> dict:
    """ Adds w_rh (Preference of patient group g originating from region r to receive care in facility h) 
    to params_system"""
    w = {}
    for r in list_regions:
        w[r.region_id] = r.facilities_affinity
    params_system["w_rh"] = w
    return params_system


def reconstruct_A_gk_from_activities(list_activities: list, params_system: dict) -> dict:
    """ Adds A_gk (num activities for pathway k of group g) to params_system"""
    validate_required_params(params_system, ["K_idx"], "Construct pathways first.")
    
    A = {g: {k: 0 for k in params_system["K_idx"][g]} for g in params_system["G"]}
    A_idx = {g: {k: [] for k in params_system["K_idx"][g]} for g in params_system["G"]}

    for a in list_activities:
        g, k = a.associated_group, a.associated_pathway
        if g in A and k in A[g]:
            A[g][k] += 1
            A_idx[g][k].append(a.activity_id)
    params_system["A_gk"] = A
    params_system["A_idx"] = A_idx
    return params_system

def reconstruct_Kg_from_pathways(list_pathways: list, params_system: dict) -> dict:
    """Adds K_g (Pathways for each patient group G) to params_system"""
    validate_required_params(params_system, ["G"], msg="Construct patient groups first")
    K_g = {}
    K_idx = {}
    for g in params_system["G"]:
        K_g[g] = len([n for n in list_pathways if n.associated_group_id == g])
        K_idx[g] = [n.pathway_id for n in list_pathways if n.associated_group_id == g]
    params_system["K_g"] = K_g 
    params_system["K_idx"] = K_idx
    return params_system



def get_K_idx(list_pathways: list, params_system: dict) -> dict:
    """ Adds list of pathways ids for each patient group G to params_system"""
    validate_required_params(params_system, ["G"], msg="Construct patient groups first")
    K_idx = {}
    for g in params_system["G"]:
        K_idx[g] = [n.pathway_id for n in list_pathways if n.associated_group_id == g]
    params_system["K_idx"] = K_idx
    
    return params_system


def reconstruct_N_gka(list_activities: list, params_system: dict):
    """
    (1) N_gka_1: All activities of pathway k of group g to be considered for potential transfers
    (2) N_gka_2: Next activity a to be considered for potential transfers after activity a of pathway k of group g
    """
    validate_required_params(params_system, ["G", "K_idx"], msg="Construct patient groups first")
    B = {g: {k: [] for k in params_system["K_idx"][g]} for g in params_system["G"]}
    N = {g: {k: {} for k in params_system["K_idx"][g]} for g in params_system["G"]}

    for a in list_activities:
        if not a.transferable:
            continue
        g, k = a.associated_group, a.associated_pathway
        B[g][k].append(a.activity_id)      
        N[g][k][a.activity_id] = a.transfer_to
        
    params_system["N_gka_1"] = B
    params_system["N_gka_2"] = N
    return params_system

def reconstruct_m_hl(list_facilities: list, params_system: dict) -> dict:
    """ Adds m_hl (Total capacity of resource type l in healthcare facilities h) to params_system"""
    m = {}
    for h in list_facilities:
        m[h.facility_id] = h.resources_capacity
    params_system["m_hl"] = m
    return params_system


def create_json_from_regions(list_regions: list, params_system: dict) -> dict:
    """Adds json parameters (R, w_rh) associated with a Region Object to params_system"""
    if "R" not in params_system:
        unique_ids = [r.region_id for r in list_regions]
        params_system["R"] = unique_ids
    if "w_rh" not in params_system:
        params_system = reconstruct_wrh(list_regions, params_system)
    return params_system

def create_json_from_resources(list_resources: list, params_system: dict) -> dict:
    """ Adds json parameters) associated with a Resource Object to params_system"""
    params_system = reconstruct_L_from_resources(list_resources, params_system)
    return params_system


def create_json_from_activities(list_activities: list, params_system: dict) -> dict:
    """ Adds json parameters (A_gk, t_gkal, N_gka1, N_gka2) associated with a Activity Object to params_system"""
    params_system = reconstruct_A_gk_from_activities(list_activities, params_system)
    params_system = reconstruct_t_gkal(list_activities, params_system)
    params_system = reconstruct_N_gka(list_activities, params_system)
    return params_system

def create_json_from_facilities(list_facilities: list, params_system: dict) -> dict:
    """Adds json parameters (H, O_gk, J_h, b_hl, m_hl) associated with a Faciliy Object to params_system"""
    params_system["H"] = [x.facility_id for x in list_facilities]
    params_system = reconstruct_O_gk(list_facilities, params_system)
    params_system = reconstruct_J_h(list_facilities, params_system)
    params_system = reconstruct_b_hl(list_facilities, params_system)
    params_system = reconstruct_m_hl(list_facilities, params_system)
    return params_system


def create_json_from_pathways(list_pathways: list, params_system: dict) -> dict:
    """ Adds json parameters (U, I_gu, Kg, c_gk, K_ids) associated with a Pathway Object to params_system"""
    params_system = reconstruct_U_from_pathways(list_pathways, params_system)
    params_system = reconstruct_I_gu(list_pathways, params_system)
    params_system = reconstruct_Kg_from_pathways(list_pathways, params_system)
    params_system = reconstruct_c_gk(list_pathways, params_system)
    params_system = get_K_idx(list_pathways, params_system)
    return params_system

def create_json_from_instance(instance: Instance, params_system: dict) -> dict:  
    """ Adds json parameters ("D", "d_gr", "Under_q_g", "Over_q_g", "Under_q_gu", "Over_q_gu" "p_transf" "delta_l" and "alpha")
    associated with an Instance object to params_system
    """
    params_system["D"] = instance.d_total
    params_system["d_gr"] = instance.d_gr
    params_system["Under_q_g"] = instance.under_q_g
    params_system["Over_q_g"] = instance.over_q_g
    params_system["Under_q_gu"] = instance.under_q_gu
    params_system["Over_q_gu"] = instance.over_q_gu
    params_system["p_transf"] = instance.p_transf
    params_system["delta_l"] = instance.delta_l
    params_system["alpha"] = instance.alpha
    return params_system 


def convert_dm_to_json(data: SystemData, params_system: dict | None = None) -> dict:
    """Calls converters for Patients, Regions, Resources, Pathways, Activities, Facilities and Instances to json
    also removes utility parameters from params_system
    """
    from backend.core.utils.data_utils import create_metadata
    if params_system is None: params_system = {}
    params_system = create_json_from_patients(data.patients, params_system)
    params_system = create_json_from_regions(data.regions, params_system)
    params_system = create_json_from_resources(data.resources, params_system)
    params_system = create_json_from_pathways(data.pathways, params_system)
    params_system = create_json_from_facilities(data.facilities, params_system)
    params_system = create_json_from_activities(data.activities, params_system)
    params_system = create_json_from_instance(data.instance, params_system)
    params_metadata = create_metadata(params_system, data.facilities, data.regions, data.patients)
    return params_system, params_metadata
