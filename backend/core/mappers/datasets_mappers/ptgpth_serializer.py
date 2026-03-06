import pandas as pd
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
from backend.core.mappers.datasets_mappers.ptgptg_utils import get_geo_polygon, summarize_geo_data, get_pop65p,\
    get_finness_info, _get_available_pathways, get_resources_capacities, _get_region_affinities


import pandas as pd
def get_Regions(df_instance: pd.DataFrame, dep_code: int) -> list[Region]:
    """Creates Region instance (cantons) given a department code (cantons are grouped by bureau de voe)"""
    gdf_cantons = get_geo_polygon()
    gdf_geo = summarize_geo_data(gdf_cantons, get_pop65p(), dep_code)
    list_regions = [Region(region_id="",
                           coordinates="",
                           facilities_affinity=_get_region_affinities()) for c in []]
    return list_regions




def get_Facilities(df_mco : pd.DataFrame, df_ssr : pd.DataFrame, dep_code: int, df_types_parcours_init: pd.DataFrame,
                   df_types_parcours: pd.DataFrame, max_transferable_in: int = 10, max_transferable_out : int = 1) -> list[Facility]:
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
            max_transferable_in = 0,
            max_transferable_out = 0,
            linked_facilities = [],
            available_pathways= _get_available_pathways()))
    #list_facilities = df_instance.apply(row_to_facility, axis=1).tolist()
    return list_facilities


def get_Instance(df_instance : pd.DataFrame) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
   
    return Instance(
            d_total = 0 ,
            d_gr = get_demand_lower_bounds(),
            under_q_g = {} ,
            over_q_g = {},
            under_q_gu = {},
            over_q_gu = {},
            p_transf = 0,
            delta_l = 0,
            alpha = 0
        )


def get_demand_lower_bounds() -> dict:
    """ Returns ``d_gr'', the lower bound on patients asssigments per patient group, per canton"""
    
    return {}


def get_Resources(df_instance : pd.DataFrame) -> list[Resource]:
    """Creates Resource object with id for unique """
    return [Resource(resource_id="")]


def get_PatientGroups(df_instance: pd.DataFrame) -> list[PatientsGroup]:
    """Creates PatientGroups """
    list_patientsGroups = []
    
    for gid in []:
        possible_pathways = _get_possible_pathways(gid)
        list_patientsGroups.append(PatientsGroup(group_id="", possible_pathways=possible_pathways))
    return list_patientsGroups


def _get_possible_pathways(gid):
    """get list of possible passways for that group"""
    return []

    

def get_Activities(list_patienGroups: list, list_pathways: list, A_idx) -> list[Activity]:
    """ get activities """
    list_activities = []
    for g in list_patienGroups:
        for k in list_pathways:
            for activity in A_idx[g][k]:
                list_activities.append(
                    Activity(activity_id= activity, associated_pathway=k,
                     associated_group=g, transferable="",
                     transfer_to="", required_resources={})
                )
    return list_activities


def get_PatientPathways(df_instance : pd.DataFrame) -> list[Pathway]:
    """ get patients pathways"""                      
    pathways = [Pathway(pathway_id= "p"+g, associated_group_id = g, quality_level = "0", list_activities= [],
                         group_benefit = 1, list_next = []) for g in []]
    return pathways



