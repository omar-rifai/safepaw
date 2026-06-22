import numpy as np 

import pandas as pd


def create_facilityLoad(results: dict, params_system: dict, by_region: bool = False,
                         by_group: bool = False,  by_pathway: bool = False, ) -> list:
    """Creates list of  FacilityLoad instances, either total per facility or per facility per region."""
    from backend.core.data_models.output_models import FacilityLoad
    
    list_facilities_loads = []
    Delta_plus = pd.DataFrame(results["Delta_plus"])
    Delta_moins = pd.DataFrame(results["Delta_moins"])


    df_loads = _compute_load(results, by_region, by_group,by_pathway, params_system)
    hl_usage = _get_hl_usage(results, params_system)

    delta_plus_value = Delta_plus.groupby(["facility","resource"], dropna=False)["value"].sum().reset_index()
    delta_moins_values = Delta_moins.groupby(["facility","resource"], dropna=False)["value"].sum().reset_index()

    Delta_plus_index = {(row.facility, row.resource): row.value for row in delta_plus_value.itertuples()}
    Delta_moins_index = {(row.facility, row.resource): row.value for row in delta_moins_values.itertuples()}
    
    capacity_cache = {str(h): calculate_facility_capacity(params_system, h) for h in params_system["H"]}
    transfers_in_cache = {str(h): get_transfers_in(h, Delta_plus_index, params_system) for h in params_system["H"]}
    transfers_out_cache = {str(h): get_transfers_out(h, Delta_moins_index, params_system) for h in params_system["H"]}

    list_facilities_loads = []
    
    for row in df_loads.itertuples(index=False):
        h = row.facility
        g = getattr(row, "group", None)
        k = getattr(row, "pathway", None)
        r = getattr(row, "region", None)
        region_coords = None
        if (not r is None):
            region_coords = [float(params_system["regions_metadata"][r]["lat"]),float(params_system["regions_metadata"][r]["lon"])]
        facility_instance = FacilityLoad(
            facility_id=h,
            coordinates= [params_system["facilities_metadata"][h]["lat"],params_system["facilities_metadata"][h]["lon"]],
            region_coordinates=region_coords,
            patient_group=g,
            patient_pathway=k,
            region_id=str(r),
            load=row.load,
            usage=hl_usage[h],
            resources_capacity=capacity_cache[h],
            transfers_in=transfers_in_cache[h],
            transfers_out=transfers_out_cache[h]
        )
        list_facilities_loads.append(facility_instance)
    return list_facilities_loads

def _compute_load(results, by_region, by_group, by_pathway, params_system):

    all_dims = ["facility", "group", "pathway", "region", "activity"]
    df_P = pd.DataFrame(results["P_gkrah"])
    sum_dims = ["activity"]
    if not by_region:
        sum_dims.append("region")
    if not by_group:
        sum_dims.append("group")
    if not by_pathway:
        sum_dims.append("pathway")    
    group_dims = [c for c in all_dims if c not in sum_dims]
    df_loads = df_P.groupby(group_dims, dropna=False)["value"].sum().reset_index()
    df_loads.rename(columns={"value": "load"}, inplace=True)
    df_loads["load"]  *= params_system["D"]
    return df_loads

def _get_hl_usage(results:dict, params_system:dict) -> dict:
    """Returns the resources (l) usage by facility (h) """
    P = pd.DataFrame(results["P_gkrah"]).groupby(["group", "pathway", "region","activity", "facility"])["value"].sum().to_dict()
    Delta_plus = pd.DataFrame(results["Delta_plus"]).groupby(["facility", "resource"])["value"].sum().to_dict()
    Delta_moins = pd.DataFrame(results["Delta_moins"]).groupby(["facility", "resource"])["value"].sum().to_dict()
    usage = {h: {l: 0 for l in params_system["L"]} for h in params_system["H"]}
    for l in params_system["L"]:
        for h in params_system["H"]:
            nominator = 0
            for g in params_system["G"]:
                for k in params_system["K_idx"][g]:
                    for r in params_system["R"]:
                        for a in params_system["A_idx"][g][k]:
                                nominator += params_system["t_gkal"][g][k][a][l] * P[(g, k, r, a, h)] * params_system["D"]
       
            denominator = params_system["m_hl"][h][l] + Delta_plus[(h,l)] - Delta_moins[(h,l)]
            usage[h][l] = nominator / denominator if denominator != 0 else 0
    return usage



def get_average_distance(results, params_system):
    """Compute the weighted average distance (in kms) across all patients"""
    import pandas as pd
    df_P = pd.DataFrame(results["P_gkrah"])
    df_loads = df_P.groupby(["region", "facility"], dropna=False)["value"].sum().reset_index()
    df_loads.rename(columns={"value": "load"}, inplace=True)

    w_rh = params_system["w_rh"]
    w_rh_flat = pd.Series({(r, h): val 
                           for r, facility_item in w_rh.items() 
                           for h, val in facility_item.items()})
    distance = df_loads.set_index(["region", "facility"])["load"] / w_rh_flat
    avg_distance = distance.sum()    
    return round(avg_distance/1000,1)


def get_transfers_in(facility, Delta_plus_index, params_system):
    return {
        l: Delta_plus_index[( facility, l)]
        for l in params_system["L"]
    }

def get_transfers_out(facility, Delta_moins_index, params_system):
    return {
        l: Delta_moins_index[(facility,l)]
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
    total_demand = params_system["D"]

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
        origin_coordinates = params_metadata["facilities"][h1]["coordinates"]
        allowed_transfers = params_system["J_h"][h1]
        total_out = calculate_total_out(results, h1, params_system) 
        transfers_distribution = total_out / len(allowed_transfers)

        for h2 in allowed_transfers:
            destination_coordinates = params_metadata["facilities"][h2]["coordinates"]
            instance_patientTransfer = PatientTransfer(patients_group_id = None,
                                                       pathway_id = None,
                                                       origin_coordinates = origin_coordinates,
                                                       destination_coordinates = destination_coordinates,
                                                       volume = transfers_distribution)
            
            list_patient_transfer.append(instance_patientTransfer) 
    return list_patient_transfer