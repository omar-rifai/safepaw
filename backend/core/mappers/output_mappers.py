import numpy as np 

def create_facilityStats(results: dict, params_system: dict, params_metadata: dict, by_region: bool = False,
                         by_group: bool = False,  by_pathway: bool = False, ) -> list:
    """Creates list of  FacilityStats instances, either total per facility or per facility per region."""
    from backend.core.data_models.output_models import FacilityStats
    
    list_facilities_loads = []
    
    Delta_plus = results["Delta_plus"]
    Delta_moins = results["Delta_moins"]
    facilities = Delta_plus.facility.values
    resources = Delta_plus.resource.values
    delta_plus_values = Delta_plus.values
    delta_moins_values = Delta_moins.values

    df_loads = _compute_load(results, by_region,by_group,by_pathway, params_system)

    Delta_plus_index = {(f,r): delta_plus_values[i, j]
                   for i, f in enumerate(facilities)
                   for j, r in enumerate(resources)}
    
    Delta_moins_index = {(f,r): delta_moins_values[i, j]
                   for i, f in enumerate(facilities)
                   for j, r in enumerate(resources)}
    
    capacity_cache = {str(h): calculate_facility_capacity(params_system, h) for h in params_system["H"]}
    transfers_in_cache = {str(h): get_transfers_in(h, Delta_plus_index, params_system) for h in params_system["H"]}
    transfers_out_cache = {str(h): get_transfers_out(h, Delta_moins_index, params_system) for h in params_system["H"]}

    list_facilities_loads = []
    
    for row in df_loads.itertuples(index=False):
        h = row.facility.split("_")[1]
        g = getattr(row, "group", None)
        k = getattr(row, "pathway", None)
        r = getattr(row, "region", None)
        if r: r=r.split("_")[1]
        
        facility_instance = FacilityStats(
            facility_id=params_metadata["facilities"][h]["name"],
            facility_type=None,
            coordinates=params_metadata["facilities"][h]["coordinates"],
            patient_group=g,
            patient_pathway=k,
            region_id=str(r),
            load=row.load,
            capacities=capacity_cache[h],
            transfers_in=transfers_in_cache[h],
            transfers_out=transfers_out_cache[h]
        )
        list_facilities_loads.append(facility_instance)
    return list_facilities_loads

def _compute_load(results, by_region, by_group, by_pathway, params_system):
    P = results["P_gkrah"]
    sum_dims = ["activity"]
    if not by_region:
        sum_dims.append("region")
    if not by_group:
        sum_dims.append("group")
    if not by_pathway:
        sum_dims.append("pathway")

    P_summed = P.sum(dim=sum_dims)
    df_loads = P_summed.to_dataframe(name="load").reset_index() 
    df_loads["load"]  *= params_system["D"][0]
    return df_loads


def get_average_distance(results, params_system):
    """Compute the weighted average distance (in kms) across all patients"""
    P_summed = results["P_gkrah"].sum(dim=["group", "pathway", "activity"])
    df_loads = P_summed.to_dataframe(name="load").reset_index() 
    h_idx = df_loads["facility"].str.split("_").str[1].astype(int).to_numpy()
    r_idx = df_loads["region"].str.split("_").str[1].astype(int).to_numpy()
    load = df_loads["load"].to_numpy()
    w_rh = np.array(params_system["w_rh"])
    distance = load / w_rh[r_idx, h_idx]
    avg_distance = distance.sum()    
    return round(avg_distance/1000,1)


def get_transfers_in(facility, Delta_plus_index, params_system):
    return {
        l: Delta_plus_index[("facility_" + str(facility), "resource_" + str(l))]
        for l in params_system["L"]
    }

def get_transfers_out(facility, Delta_moins_index, params_system):
    return {
        l: Delta_moins_index[("facility_" + str(facility), "resource_" + str(l))]
        for l in params_system["L"]
    }

def calculate_facility_capacity(params_system, facility_id):
    capacities = {}
    for l in params_system["L"]:
        capacities[l] = params_system["m_hl"][facility_id][l]
    return capacities


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