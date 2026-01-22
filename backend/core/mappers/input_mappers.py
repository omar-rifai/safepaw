from backend.core.data_models.input_models import Instance, SystemData

def validate_required_params(params, required_keys, msg):
    missing = [k for k in required_keys if k not in params]
    if missing:
        raise KeyError(f"Missing required parameters: {missing}. {msg}")


def create_json_from_patients(list_patients: list, params_system: dict) -> dict:
    """ Adds group ids as indices (G) and as strings (G_ids) to params_system"""
    params_system["G_ids"] = list(dict.fromkeys(x.group_id for x in list_patients))
    params_system["G"] = list(range(len(params_system["G_ids"])))
    return params_system


def reconstruct_L_from_resources(list_resources: list, params_system: dict) -> dict:
    """ Adds Resource types (L) to params_system"""
    list_resources = list(dict.fromkeys([r.resource_type for r in list_resources]))
    params_system["L"] = list(range(len(list_resources)))
    return params_system


def reconstruct_I_gu(list_pathways: list, params_system: dict) -> dict:
    """ Adds Set of pathways available to group g that fall under care quality level u to params_system"""
    validate_required_params(params_system, ["G_ids"], "Construct patient groups first.")       
    I_gu = []
    for i,g in enumerate(params_system["G_ids"]):
        I_g = []
        for u in range(params_system["U"][i]):
            I_g.append([i for i,x in enumerate([x for x in list_pathways if x.associated_group_id == g])
                  if x.quality_level==str(u)])
        I_gu.append(I_g)
    params_system["I_gu"] = I_gu
    return params_system


def reconstruct_c_gk(list_pathways: list, params_system: dict) -> dict:
    """ Adds c_gk ( Benefit score of assigning a patient from group g with the care pathway k) to params_system"""
    validate_required_params(params_system, ["G_ids"], "Construct patient groups first.")
    c_gk = []
    max_g = max(params_system["K_g"])
    for g in params_system["G_ids"]:
        c_g = [x.group_benefit for x in sorted(
            [x for x in list_pathways if x.associated_group_id == g],
            key=lambda p: p.pathway_id
      )]
        padded_cg = c_g + [0] * (max_g - len(c_g))
        c_gk.append(padded_cg)
    params_system["c_gk"] = c_gk
    return params_system


def reconstruct_U_from_pathways(list_pathways: list, params_system: dict) -> dict:
    """ Adds U (Quality level u among the Ug quality levels of care pathways of group g) to params_system"""
    validate_required_params(params_system, ["G_ids"], "Construct patient groups first.")
    U_g = []
    for g in params_system["G_ids"]:
        U_g.append(len(set([k.quality_level for k in list_pathways if k.associated_group_id == g])))
    params_system["U"] = U_g
    return params_system


def reconstruct_O_gk(list_facilities: list, params_system: dict) -> dict:
    """ Adds O_g,k (Set of healthcare facilities able to treat patient group g following pathway k) to params_system"""
    validate_required_params(params_system, ["K_ids", "G"], "Construct patient groups and pathways first")
    O_gk = []    
    for _, g in enumerate(params_system["G_ids"]):
        O_g = []
        for k in params_system["K_ids"][g]:
            O_k = [i for i,h in enumerate(list_facilities) if k in h.available_pathways]
            O_g.append(O_k)
        O_gk.append(O_g)
    
    params_system["O_gk"] = O_gk
    return params_system


def reconstruct_J_h(list_facilities: list, params_system: dict) -> dict:
    """ Adds J_h (Set of healthcare facilities to which patients from facility h can be transferred) to params_system"""
    def get_facility_index(list_facilities, f_id):
        for i,facility in enumerate(list_facilities):
            if facility.facility_id == f_id:
                return i
    
    J_h = [[get_facility_index(list_facilities,f) for f in h.linked_facilities if f is not h] for h in list_facilities]
    params_system["J_h"] = J_h
    return params_system


def reconstruct_b_hl(list_facilities: list, params_system: dict) -> dict:
    """ Adds b_hl_in and b_hl_out (Maximum proportions of resource type l transferable to and from facility h) to params_system"""
    b_hl_in = []
    b_hl_out = []
    for h in list_facilities:
        # Ensure values are in order of resource indices
        ordered_values_in = [h.max_transferable_in[k] for k in sorted(h.max_transferable_in.keys(), key=str)]
        ordered_values_out = [h.max_transferable_out[k] for k in sorted(h.max_transferable_out.keys(), key=str)]
        b_hl_in.append(ordered_values_in)
        b_hl_out.append(ordered_values_out)
    params_system["b_hl_in"] = b_hl_in
    params_system["b_hl_out"] = b_hl_out

    return params_system

def _compute_max_sizes(list_activities: list, params_system: list) -> tuple[int, int, int]:
    """ Computes the maximum number of (1) pathways across groups, (2) activities in pathways and (3) resources across activities"""
    validate_required_params(params_system, ["G_ids"], "Construct patient groups first.")
    A_gk = params_system["A_gk"]
    # Maximum number of pathways across all groups
    max_k_len = max(len(A_gk[i]) for i, g in enumerate(params_system["G_ids"]))
    # Maximum number of activities across all pathways
    max_a_len =  max((max(row) for row in A_gk), default=0)
    # Maximum number of resources across all activities
    max_l_len = max(len(a.required_resources) for a in list_activities)
    return max_k_len, max_a_len, max_l_len


def _pad_activity_list(required_resources: list, max_l_len: int) -> list:
    """Pad the list of required resources of an activity with 0 (to max number of resources across activities)"""
    values = list(required_resources.values())
    return values  + [0] * (max_l_len - len(values))


def reconstruct_t_gkal(list_activities: list, params_system: dict) -> dict:
    """Adds t_gkal (Consumption of resource l required to perform care activity a of pathway k of group g) to params_system"""
    validate_required_params(params_system, ["G", "K_ids"], "Construct patient groups and pathways first.")
    max_k_len, max_a_len, max_l_len = _compute_max_sizes(list_activities, params_system)
    t_gkal = []
    
    for _, g in enumerate(params_system["G_ids"]):
        list_t_g = []
        
        for k in params_system["K_ids"][g]:
            list_t_k = []
            concerned_activities = [a for a in list_activities if a.associated_group == g and a.associated_pathway == str(k)]
            
            for a in concerned_activities:
                list_t_k.append(_pad_activity_list(a.required_resources, max_l_len))
           
            # Pad second-level list
            while len(list_t_k) < max_a_len:
                list_t_k.append([0]*max_l_len)
            list_t_g.append(list_t_k)
       
        # Pad first-level list
        while len(list_t_g) < max_k_len:
            list_t_g.append([[0]*max_l_len for _ in range(max_a_len)])
        t_gkal.append(list_t_g)

    params_system["t_gkal"] = t_gkal
    return params_system


def reconstruct_wrh(list_regions: list, params_system: dict) -> dict:
    """ Adds w_rh (Preference of patient group g originating from region r to receive care in facility h) 
    to params_system
    """
    w_rh = []
    for r in list_regions:
        region_affinity = [r.facilities_affinity[k] for k in r.facilities_affinity.keys()]
        w_rh.append(region_affinity)
    params_system["w_rh"] = w_rh
    return params_system


def reconstruct_A_gk_from_activities(list_activities: list, params_system: dict) -> dict:
    """ Adds A_gk (num activities for pathway k of group g) to params_system"""
    validate_required_params(params_system, ["K_ids"], "Construct pathways first.")
    params_system["A_gk"] = [
        [sum(1 for a in list_activities
                if a.associated_group == g
                and a.associated_pathway == str(k))
            for k in params_system["K_ids"][g]]
        for _, g in enumerate(list(dict.fromkeys([a.associated_group for a in list_activities])))]
    return params_system


def reconstruct_Kg_from_pathways(list_pathways: list, params_system: dict) -> dict:
    """Adds K_g (Pathways for each patient group G) to params_system"""
    validate_required_params(params_system, ["G_ids"], msg="Construct patient groups first")
    list_K_g = [len([n for n in list_pathways if n.associated_group_id == g]) for g in params_system["G_ids"]]
    params_system["K_g"] = list_K_g 
    return params_system



def get_K_ids(list_pathways: list, params_system: dict) -> dict:
    """ Adds list of pathways ids for each patient group G to params_system"""
    validate_required_params(params_system, ["G_ids"], msg="Construct patient groups first")
    K_ids = {}
    for g in params_system["G_ids"]:
        K_ids[g] = [n.pathway_id for n in list_pathways if n.associated_group_id == g]
    params_system["K_ids"] = K_ids
    
    return params_system


def reconstruct_N_gka(list_activities: list, params_system: dict):
    """
    (1) N_gka_1: All activities of pathway k of group g to be considered for potential transfers
    (2) N_gka_2: Next activity a to be considered for potential transfers after activity a of pathway k of group g
    """
    validate_required_params(params_system, ["G_ids"], msg="Construct patient groups first")
    unique_pathways = list(dict.fromkeys([a.associated_pathway for a in list_activities]))
    list_Ngka1 = []
    list_Ngka2 = []
    for g in params_system["G_ids"]:
        list_Ng1 = []
        list_Ng2 = []
        for k in range(len(unique_pathways)):
            transferable = [int(a.activity_id) for a in list_activities if a.associated_pathway == str(k) and a.associated_group == g and a.transferable]        
            transfer_to = [int(a.transfer_to) for a in list_activities if a.associated_pathway == str(k) and a.associated_group == g and a.transferable]
            if transferable:
                list_Ng1.append(transferable)
                list_Ng2.append(transfer_to)
            else:
                 list_Ng1.append([])
                 list_Ng2.append([])
        list_Ngka1.append(list_Ng1)
        list_Ngka2.append(list_Ng2)
    params_system["N_gka_1"] = list_Ngka1
    params_system["N_gka_2"] = list_Ngka2

    return params_system

def reconstruct_m_hl(list_facilities: list, params_system: dict) -> dict:
    """ Adds m_hl (Total capacity of resource type l in healthcare facilities h) to params_system"""
    m_hl = []
    for h in list_facilities:
        m_hl.append(list(dict.fromkeys(h.resources_capacity.values())))
    params_system["m_hl"] = m_hl
    return params_system


def create_json_from_regions(list_regions: list, params_system: dict) -> dict:
    """Adds json parameters (R, w_rh) associated with a Region Object to params_system"""
    if "R" not in params_system:
        unique_ids = [r.region_id for r in list_regions]
        params_system["R"] = list(range(len(unique_ids)))
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
    params_system["H"] = list(range(len(list_facilities)))
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
    params_system = get_K_ids(list_pathways, params_system)
    return params_system

def create_json_from_instance(instance: Instance, params_system: dict) -> dict:  
    """ Adds json parameters ("D", "d_gr", "Under_q_g", "Over_q_g", "Under_q_gu", "Over_q_gu" "p_transf" "delta_l" and "alpha")
    associated with an Instance object to params_system
    """
    params_system["D"] = [instance.d_total]
    params_system["d_gr"] = instance.d_gr
    params_system["Under_q_g"] = instance.under_q_g
    params_system["Over_q_g"] = instance.over_q_g
    params_system["Under_q_gu"] = instance.under_q_gu
    params_system["Over_q_gu"] = instance.over_q_gu
    params_system["p_transf"] = [instance.p_transf]
    params_system["delta_l"] = instance.delta_l
    params_system["alpha"] = [instance.alpha]
    return params_system 


def normalize_params(params_system: dict) -> dict:
    """Remove parameters not used in optimization"""
    params_system.pop('G_ids', None)
    params_system.pop('K_ids', None)
    return params_system

def convert_dm_to_json(data: SystemData, params_system: dict | None = None) -> dict:
    """Calls converters for Patients, Regions, Resources, Pathways, Activities, Facilities and Instances to json
    also removes utility parameters from params_system
    """
    from backend.core.utils.data_utils import create_metadata
    params_metadata = create_metadata(data.facilities, data.regions, data.patients)
    if params_system is None: params_system = {}
    params_system = create_json_from_patients(data.patients, params_system)
    params_system = create_json_from_regions(data.regions, params_system)
    params_system = create_json_from_resources(data.resources, params_system)
    params_system = create_json_from_pathways(data.pathways, params_system)
    params_system = create_json_from_facilities(data.facilities, params_system)
    params_system = create_json_from_activities(data.activities, params_system)
    params_system = create_json_from_instance(data.instance, params_system)
    params_system = normalize_params(params_system)
    return params_system, params_metadata


def run_legacy_reader(data_file: str) -> dict:
    """Converter from legacy format into json format"""
    import backend.core.utils.legacy_data_utils as lr
    G, K_g, R, A_gk, H, L, c_gk, alpha, w_rh, D, d_gr, t_gkal, m_hl,\
    Under_q_g, Over_q_g, U, I_gu, Under_q_gu, Over_q_gu, O_gk, J_h, p_transf, b_hl_in, b_hl_out,\
    delta_l, N_gka_1, N_gka_2 = lr.readCompleteDataFile(data_file)
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
        "b_hl_in": b_hl_in, # max proportions of resources of type l transferable to facility h
        "b_hl_out": b_hl_out # max proportions of resources of type l transferable from facility h
    }
    return params_system
