
def create_facilityStats(results: dict, params_system: dict, params_metadata: dict, by_region: bool = False,
                         by_group: bool = False,  by_pathway: bool = False, ) -> list:
    """Creates list of  FacilityStats instances, either total per facility or per facility per region."""
    from backend.core.data_models.output_models import FacilityStats
    list_facilities_loads = []
    for h in params_system["H"]:  
        facility_coordinates = params_metadata["facilities"][str(h)]["coordinates"]
        regions = [None] if not by_region else params_system["R"]
        groups = [None] if not by_group else params_system["G"]
        for g in groups:
            pathways = [None] if not by_pathway else params_system["A_gk"][g]
            for k in pathways:
                for r in regions: 
                    curr_load = calculate_facility_load(results, params_system, dims = {"facility":h, "region": r,
                                                    "group": g, "pathway": k})
                    facility_instance = FacilityStats(
                        facility_id= params_metadata["facilities"][str(h)]["name"],
                        facility_type=None,
                        coordinates=facility_coordinates,
                        patient_group=None,
                        patient_pathway=None,
                        region_id= str(r),
                        load = curr_load ,
                        capacities = calculate_facility_capacity(params_system, h),
                        transfers_in = get_transfers_in(results=results, facility=h, params_system=params_system),
                        transfers_out = get_transfers_out(results=results, facility=h, params_system=params_system))
                    list_facilities_loads.append(facility_instance)
    return list_facilities_loads


def get_transfers_in(results, facility, params_system):
    transfers_in = {}
    for l in params_system["L"]:
        transfers_in[l] = results["Delta_plus"].sel({"facility": "facility_" + str(facility), "resource": "resource_" + str(l) }).item()
    return transfers_in


def get_transfers_out(results, facility, params_system):
    transfers_out = {}
    for l in params_system["L"]:
        transfers_out[l] = results["Delta_moins"].sel({"facility": "facility_" + str(facility), "resource": "resource_" + str(l) }).item()

    return  transfers_out

def calculate_facility_capacity(params_system, facility_id):
    capacities = {}
    for l in params_system["L"]:
        capacities[l] = params_system["m_hl"][facility_id][l]
    return capacities

def calculate_facility_load(results : dict, params_system : dict, dims) -> dict:
    """Calculated the used capacity by resource / facility"""

    total_demand = params_system["D"][0]

    all_dims = ["group", "pathway", "region", "facility"]
    sum_dims = [x for x in all_dims if dims[x] is None]  + ["activity"]
    sel_dims = {x: f"{x}_{dims[x]}" for x in all_dims if dims[x] is not None}

    frac_used = results["P_gkrah"]\
            .sel(**sel_dims)\
                .sum(dim=sum_dims).item()
 
    load =  frac_used * total_demand 

    return load

def calculate_total_out(results:dict, h_id, params_system: dict) -> int:
    """ Return the number of patients transfered from one facililty to another"""
    h_id = "facility_" + str(h_id)
    total_demand = params_system["D"][0]

    perc_out = results["Q_gkrah"].sel(facility=h_id).sum(dim=["group", "pathway", "region", "activity"]).item()
    perc_tot = results["P_gkrah"].sel(facility=h_id).sum(dim=["group", "pathway", "region", "activity"]).item() 

    demand_h = total_demand * perc_tot    
    total_out = demand_h * perc_out
    
    return total_out


def create_patientTransfers(results: dict, params_system: dict, params_metadata : dict) -> list:
    """ Returns a list of patientTransfer Instances """
    from backend.core.data_models.output_models import PatientTransfer
    list_patient_transfer = []
    for h1 in params_system["H"]:
        origin_coordinates = params_metadata["facilities"][str(h1)]["coordinates"]
        allowed_transfers = params_system["J_h"][h1]
        total_out = calculate_total_out(results, h1, params_system) 
        transfers_distribution = total_out / len(allowed_transfers)

        for h2 in allowed_transfers:
            destination_coordinates = params_metadata["facilities"][str(h2)]["coordinates"]
            instance_patientTransfer = PatientTransfer(patients_group_id = None,
                                                       pathway_id = None,
                                                       origin_coordinates = origin_coordinates,
                                                       destination_coordinates = destination_coordinates,
                                                       volume = transfers_distribution)
            
            list_patient_transfer.append(instance_patientTransfer) 
    return list_patient_transfer