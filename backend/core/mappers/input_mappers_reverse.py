from backend.core.data_models.input_models import SystemData, PatientsGroup, Region, Resource, Pathway, Facility, Activity, Instance

def create_Patients_from_json(params_system: dict) -> list:
    """Returns list of Patient Objects from model params"""
    list_patients = []
    for g in params_system["G"]:
        list_patients.append(PatientsGroup(group_id=g, possible_pathways=params_system["K_idx"][g]))
    return list_patients

def create_Regions_from_json(params_system: dict) -> list:
    """Returns list of Region Objects from model params"""
    list_regions = []
    for r in params_system["R"]:
        list_regions.append(Region(region_id=r, coordinates=[], dep_code=params_system["regions_metadata"][r]["dep_code"],
                                   comm_code=params_system["regions_metadata"][r]["comm_code"],
                                   can_code= params_system["regions_metadata"][r]["can_code"],
                                   facilities_affinity=params_system["w_rh"][r]))
    return list_regions

def create_Resources_from_json(params_system: dict) -> list:
    """Returns list of Resources Objects from model params"""
    list_resources = []
    for l in params_system["L"]:
        list_resources.append(Resource(resource_id=l))
    return list_resources

def create_Pathways_from_json(params_system: dict) -> list:
    """Returns list of Pathway Objects from model params"""

    def get_quality_level(g,k):
        for u in params_system["U_idx"][g]:
            if k in params_system["I_gu"][g][u]:
                return u

    list_pathways = []
    k_ids = params_system["K_g"].keys()
    for k in k_ids:
        for g in params_system["G"]:
            if k in params_system["K_idx"][g]:
                list_pathways.append(Pathway(pathway_id=k, associated_group_id=g,
                                            quality_level=get_quality_level(g,k),
                                            list_activities=params_system["A_idx"][g][k],
                                            group_benefit=params_system["c_gk"][g][k]))

    return list_pathways

def create_Facilities_from_json(params_system: dict) -> list:
    """Returns list of PatientsGroup Objects from model params"""

    def get_available_pathways(h):
        available_pathways = []
        for g in params_system["G"]:
            for k in params_system["K_idx"][g]:
                if h in params_system["O_gk"][g][k]:
                    available_pathways.append(k)
        return available_pathways
    
    list_facilities = []
    for h in params_system["H"]:
        list_facilities.append(Facility(facility_id=h,
                                        facility_name=params_system["facilities_metadata"][h]["name"],
                                        facility_type=params_system["facilities_metadata"][h]["type"],
                                        region_id=params_system["facilities_metadata"][h]["region_id"],
                                        coordinates=params_system["facilities_metadata"][h]["coords"],
                                        resources_capacity= params_system["m_hl"][h],
                                        nbr_visits=params_system["facilities_metadata"][h]["nbr_visits"],
                                        available_pathways=get_available_pathways(h),
                                        linked_facilities=params_system["J_h"][h],
                                        max_transferable_in=params_system["b_hl_in"][h],
                                        max_transferable_out= params_system["b_hl_out"][h]))
    return list_facilities

def create_Activities_from_json(params_system: dict) -> list:
    """Returns list of Activity Objects from model params"""
    list_activities = []
    for g in params_system["G"]:
        for k in params_system["K_idx"][g]:
            for a in params_system["A_idx"][g][k]:
                is_transferable = (a in params_system["N_gka_1"][g][k])
                transfer_to = None
                if is_transferable: transfer_to = params_system["N_gka_2"][g][k][a]
                list_activities.append(Activity(activity_id=a, associated_pathway=k,
                                            associated_group=g, transferable= is_transferable,
                                            transfer_to= transfer_to,
                                            required_resources=params_system["t_gkal"][g][k][a]))
    return list_activities

def create_Instance_from_json(params_system: dict) -> list:
    """Returns Instance Object from model params"""
    instance = Instance(d_total= params_system["D"],d_gr= params_system["d_gr"], under_q_g=params_system["Under_q_g"],over_q_g=params_system["Over_q_g"],
                        under_q_gu=params_system["Under_q_gu"],over_q_gu= params_system["Over_q_gu"], p_transf=params_system["p_transf"],
                         delta_l= params_system["delta_l"], alpha=params_system["alpha"])
    return instance

def convert_dm_from_json(params_system: dict) ->SystemData:
    """Retrieve Patients, Regions, Resources, Pathways, Activities, Facilities and Instances from json"""
    if params_system is None: params_system = {}
    list_patients = create_Patients_from_json(params_system)
    list_regions = create_Regions_from_json(params_system)
    list_resources = create_Resources_from_json(params_system)
    list_pathways = create_Pathways_from_json(params_system)
    list_facilities = create_Facilities_from_json(params_system)
    list_activities = create_Activities_from_json(params_system)
    instance = create_Instance_from_json( params_system)
    ModelInstance = SystemData(regions=list_regions,resources=list_resources, facilities=list_facilities,patients=list_patients,
                               pathways=list_pathways, activities=list_activities, instance=instance)
    return ModelInstance