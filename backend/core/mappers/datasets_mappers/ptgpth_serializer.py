import pandas as pd
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
from backend.core.mappers.datasets_mappers.ptgpth_utils import get_geo_polygon, summarize_geo_data, get_pop65p,\
    get_finness_info, get_resources_capacities, get_region_affinities, get_required_resources,\
    get_transfer_to, get_transferable, get_activities_per_group_pathway, get_demand_lower_bounds, list_resources


import pandas as pd
def get_Regions(dep_code: int, df_ssr: pd.DataFrame, df_mco:pd.DataFrame) -> list[Region]:
    """Creates Region instance (cantons) given a department code (cantons are grouped by bureau de vote)"""
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    df_finess = get_finness_info(df_mco, df_ssr, gdf_cantons)
    affinities = get_region_affinities(gdf_geo,df_finess)
    list_regions = [Region(region_id=row["can_code"],
                           coordinates=[row["geometry"].centroid.x, row["geometry"].centroid.y],
                           facilities_affinity=affinities[row["can_code"]] )for i,row in gdf_geo.iterrows()]
    return list_regions




def get_Facilities(df_mco : pd.DataFrame, df_ssr : pd.DataFrame, dep_code: int, df_types_parcours_init: pd.DataFrame,
                   df_types_parcours: pd.DataFrame, list_resources: list) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids """
    list_facilities = []
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    df_finess = get_finness_info(df_mco, df_ssr, gdf_geo)
    list_finess = list(df_finess["nofinesset"].unique())
    list_finess.append("DOM")
    m_hl = get_resources_capacities(list_finess, df_types_parcours_init, df_ssr, df_mco, df_types_parcours)
    
    for row in df_finess.itertuples():     
        list_facilities.append(Facility(
            facility_id = row.nofinesset,
            facility_name = "" ,
            region = row.can_code,
            coordinates =[row.lat, row.lon] , 
            resources_capacity = m_hl[row.nofinesset] ,
            max_transferable_in = {l: 0 if l != "finance" else 1 for l in list_resources },
            max_transferable_out = {l: 0 if l != "finance" else 1 for l in list_resources },
            linked_facilities = list_finess,
            available_pathways= df_types_parcours_init["SSR_TYPE"].unique()))
    return list_facilities


def get_Instance(gdf_summary: pd.DataFrame, df_types_parcours: pd.DataFrame, 
                 list_groups_ids: list, list_resources: list) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
   
    return Instance(
            d_total = 1464 ,
            d_gr = get_demand_lower_bounds(gdf_summary, df_types_parcours),
            under_q_g = {g : 0 for g in list_groups_ids} ,
            over_q_g = {g : 1 for g in list_groups_ids},
            under_q_gu = {g : {"0": 1} for g in list_groups_ids},
            over_q_gu = {g : {"0": 1} for g in list_groups_ids},
            p_transf = 1,
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


def get_Activities(list_patienGroups: list, list_pathways: list, A_idx: dict) -> list[Activity]:
    """ get activities """
    list_activities = []
    dict_required_resources = get_required_resources(A_idx)
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
                     transfer_to= transfer_to, required_resources= dict_required_resources[g][k][a]))
    return list_activities


def get_PatientPathways(list_pathways_ids: list, list_groups: list) -> list[Pathway]:
    """ get patients pathways"""
    A_idx = get_activities_per_group_pathway(list_groups, list_pathways_ids)
    list_pathways = []
    for g in list_groups:                      
        list_pathways.extend([Pathway(pathway_id=p_id, associated_group_id = g, quality_level = "0", list_activities= A_idx[g][p_id],
                            group_benefit = 1) for p_id in list_pathways_ids])
    return list_pathways



