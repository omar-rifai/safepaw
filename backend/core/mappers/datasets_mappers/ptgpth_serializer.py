import pandas as pd
import typer
import os
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
from backend.core.mappers.datasets_mappers.ptgpth_utils import load_data, get_geo_polygon, summarize_geo_data, get_pop65p,\
    get_finess_info, get_resources_capacities, get_region_affinities, get_required_resources, get_transfer_to, get_transferable,\
    get_activities_per_group_pathway, get_demand_lower_bounds, list_resources, add_orth_facility, add_dom_facility

pathway_benefit = {"HC":1, "DOM":2, "HC_HDJ": 1.25, "HDJ":1.5}

def get_Regions(df_finess: pd.DataFrame, gdf_summary: pd.DataFrame) -> list[Region]:
    """Creates Region instance (cantons) given a department code (cantons are grouped by bureau de vote)"""
   
    affinities = get_region_affinities(gdf_summary, df_finess)
    list_regions = [Region(region_id=row["can_code"],
                           coordinates=[row["geometry"].centroid.x, row["geometry"].centroid.y],
                           facilities_affinity=affinities[row["can_code"]] )for _,row in  gdf_summary.iterrows()]
    return list_regions


def get_Facilities(df_mco : pd.DataFrame, df_ssr : pd.DataFrame,  df_finess:pd.DataFrame,  df_types_parcours: pd.DataFrame, dep_code: int,
                    t_gkal: dict, list_resources: list, list_pathways: list, p_orth:float, multiplier=1.0) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids """

    list_facilities = []
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    #df_finess = get_finess_info(df_mco, df_ssr, gdf_geo)
    list_finess = list(df_finess["nofinesset"].unique())
    list_finess.extend(["DOM", "ORTH"])
    m_hl = get_resources_capacities(t_gkal, list_finess, df_types_parcours, df_ssr, df_mco, multiplier)

    for row in df_finess.itertuples():     
        list_facilities.append(Facility(
            facility_id = row.nofinesset,
            facility_name = "" ,
            model_region = row.can_code,
            coordinates =[row.lat, row.lon] , 
            resources_capacity = m_hl[row.nofinesset] ,
            max_transferable_in = {l: 0 if l != "finance" else 1000 for l in list_resources },
            max_transferable_out = {l: 0 if l != "finance" else 1000 for l in list_resources },
            linked_facilities = list_finess,
            available_pathways= df_types_parcours["SSR_TYPE"].unique()))
    list_facilities = add_dom_facility(list_facilities, list_pathways, list_finess, gdf_geo, m_hl)
    list_facilities = add_orth_facility(list_facilities, list_pathways, list_finess, gdf_geo, p_orth)
    return list_facilities


def get_Instance(gdf_summary: pd.DataFrame, df_types_parcours: pd.DataFrame, 
                 list_groups_ids: list, list_resources: list, p_transf: float, quality_levels:dict) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
    if len(set(quality_levels.values())) > 1 : quality_objectives = {quality_levels["DOM"]: 0.75,
                                                                    quality_levels["HDJ"]:0.05, quality_levels["HC_HDJ"]:0.05,
                                                                    quality_levels["HC"]:0.2 }
    else: quality_objectives = {"0": 1}

    return Instance(
            d_total = df_types_parcours["nb"].sum(),
            d_gr = get_demand_lower_bounds(gdf_summary, df_types_parcours),
            under_q_g = {g : 0 for g in list_groups_ids} ,
            over_q_g = {g : 1 for g in list_groups_ids},
            under_q_gu = {g : quality_objectives for g in list_groups_ids},
            over_q_gu = {g :  quality_objectives for g in list_groups_ids},
            p_transf = p_transf,
            delta_l = {l: 1 for l in list_resources},
            alpha = 0.0125
        )

def get_Resources(list_resources: list) -> list[Resource]:
    """Creates Resource object with id for unique """
    return [Resource(resource_id=l) for l in list_resources]


def get_PatientGroups(list_group_ids: list, list_pathways: list) -> list[PatientsGroup]:
    """Creates PatientGroups. All groups have all pathways"""
    list_patientsGroups = []
    for gid in list_group_ids:
        list_patientsGroups.append(PatientsGroup(group_id=gid, possible_pathways=list_pathways))
    return list_patientsGroups


def get_Activities(t_gkal: dict, list_patienGroups: list, list_pathways: list, A_idx: dict) -> list[Activity]:
    """ get activities """
    list_activities = []
    tranferable_activities = get_transferable(A_idx)
    transfer_to_activities = get_transfer_to(A_idx)
    for g in list_patienGroups:
        for k in list_pathways:
            for a in A_idx[g][k]:
                if a in transfer_to_activities[g][k]: 
                    transfer_to = transfer_to_activities[g][k][a]
                else: transfer_to = ""
                list_activities.append(
                    Activity(activity_id= a, associated_pathway=k,
                     associated_group=g, transferable=a in tranferable_activities[g][k],
                     transfer_to= transfer_to, required_resources= t_gkal[g][k][a]))
    return list_activities


def get_PatientPathways(A_idx: dict, list_pathways_ids: list, list_groups: list, pathway_benefit:dict, quality_levels:dict) -> list[Pathway]:
    """ get patients pathways"""
    
    list_pathways = [] 
    for g in list_groups:                      
        list_pathways.extend([Pathway(pathway_id=p_id, associated_group_id = g, quality_level = quality_levels[p_id], list_activities= A_idx[g][p_id],
                            group_benefit = pathway_benefit[p_id]) for p_id in list_pathways_ids])
    return list_pathways

def get_data(dep_code: str):
    """prepare the raw data in DataFrames."""
    df_types_parcours, df_mco, df_ssr = load_data([int(dep_code)])
    df_types_parcours = df_types_parcours.groupby(["sej_type", "type_parcours", "SSR_TYPE"], as_index=False)["nb"].sum()
    df_types_parcours = df_types_parcours[df_types_parcours["nb"].fillna(0) >= 3]
    gdf_geo =  get_geo_polygon()
    gdf_summary = summarize_geo_data(gdf_geo, get_pop65p(), dep_code)
    df_finess = get_finess_info(df_mco, df_ssr, gdf_geo)
    return df_types_parcours, df_mco, df_ssr, gdf_summary, df_finess


def serialize_ptgpth(
        dep_code: str = typer.Option("42", help="department code"),
        p_transf: float = typer.Option(1, help="Maximum allowed patitiens transfer percentage"),
        p_orth:float = typer.Option(0, help="Orthopedic center percentage additional resources"),
        resources_mult: float = typer.Option(1, help="Multiplier for the available resources"),
        quality_requirement: bool = typer.Option(False, help="Impose a strict distribution of patients to pathways as described in article."),
        save_params: bool = typer.Option(True)
        ):
    return serialize_ptgpth_core(dep_code, p_transf, p_orth, resources_mult, quality_requirement, save_params)


def serialize_ptgpth_core(
        dep_code: str = "42",
        p_transf: float = 1,
        p_orth:float = 0,
        resources_mult: float = 1,
        quality_requirement: bool = False,
        save_params: bool = True):
    """Serialize PTG PTH Data and write to file"""
    
    from backend.core.data_models.input_models import SystemData
    from backend.core.mappers.input_mappers import convert_dm_to_json
    import json
 
    if quality_requirement:
        quality_levels = {"DOM":"1","HC":"3","HDJ":"2","HC_HDJ":"2"}
    else:
        quality_levels = {"DOM":"0","HC":"0","HDJ":"0","HC_HDJ":"0"}

    df_types_parcours, df_mco, df_ssr, gdf_summary, df_finess = get_data(dep_code)
  
    list_patientGroups = list(set(df_types_parcours['sej_type'] +  "_" + df_types_parcours['type_parcours'].str.replace(" + ", "_", regex=False)))
    list_pathways =  list(df_types_parcours["SSR_TYPE"].unique())
    A_idx = get_activities_per_group_pathway(list_patientGroups, list_pathways)
    t_gkal = get_required_resources(A_idx)

    list_Regions = get_Regions(df_finess, gdf_summary)
    list_Resources = get_Resources(list_resources)
    list_PatientsGroups = get_PatientGroups(list_patientGroups, list_pathways )
    list_Activities = get_Activities(t_gkal, list_patientGroups, list_pathways, A_idx)
    list_Facilities = get_Facilities(df_mco, df_ssr, df_finess, df_types_parcours, dep_code, t_gkal, list_resources, list_pathways,
                                    p_orth, resources_mult)
    list_Pathways = get_PatientPathways(A_idx, list_pathways, list_patientGroups, pathway_benefit, quality_levels)
    instance = get_Instance(gdf_summary, df_types_parcours, list_patientGroups, list_resources, p_transf, quality_levels)
    sys_data = SystemData(regions = list_Regions, resources=list_Resources, facilities=list_Facilities,
                          patients=list_PatientsGroups , pathways=list_Pathways, activities= list_Activities, instance=instance)
    params_system, _ = convert_dm_to_json(sys_data)
    
    if save_params:
        os.makedirs("experiments", exist_ok=True)
        with open("experiments/params_ptgpth_" + str(dep_code) + "_" + str(round(p_transf,2))+ "_" + str(round(p_orth,2))+ "_" + str(round(resources_mult,2)) + ".json", "w") as fp:
            json.dump(params_system, fp)

    return params_system    

if __name__ == "__main__":
     import pyproj
     pyproj.datadir.set_data_dir(pyproj.datadir.get_data_dir())
     typer.run(serialize_ptgpth)