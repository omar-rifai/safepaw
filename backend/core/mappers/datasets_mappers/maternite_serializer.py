import pandas as pd
from typing import Union
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
import geopandas as gpd
import numpy as np

DF_LABOURS_ALL = pd.read_csv("backend/data/open_data/summary_maternity_labours.csv", low_memory=False)
DF_GEO_COMMS = gpd.read_parquet("backend/data/open_data/communes-50m.parquet")
DF_GEO_COMMS_METERS= DF_GEO_COMMS.to_crs(epsg=2154)
centroids_m = DF_GEO_COMMS_METERS.geometry.centroid
centroids_wgs84 = centroids_m.to_crs(epsg=4326)
# Precompute centroids once
DICT_COMM_CENTROIDS = dict(zip(
    DF_GEO_COMMS["code"],
    np.vstack([centroids_wgs84.x.values,
               centroids_wgs84.y.values]).T
))


def get_Regions(df_instance: pd.DataFrame) -> list[Region]:
    """Creates `Region` instance using public data on French communes (Commune code and coordinates)"""
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance["dep_code"])]
    df_geo_comms = DF_GEO_COMMS_METERS[DF_GEO_COMMS_METERS["code"].isin(df_labours["comm_code"])]
    affinities_dict = _get_affinities(df_instance, df_geo_comms)
    communes_ids = list(df_geo_comms["code"].drop_duplicates().sort_values())
    list_regions = [Region(region_id=c_id, coordinates=DICT_COMM_CENTROIDS[c_id], facilities_affinity=affinities_dict[c_id]) for c_id in communes_ids]
    return list_regions


def get_Facilities(df_instance : pd.DataFrame, max_transferable_in : int = 10, max_transferable_out : int = 1) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids with (bed/days) as resource 
    and availiable pathways dependent on to the facility type (1,2a,2b,3)"""
    all_ids = df_instance["nofinesset"].sort_values().to_list()
    linked_facilities_dict = {fid: [x for x in all_ids if x != fid] for fid in all_ids} 
    def row_to_facility(row):
        return Facility(
            facility_id = str(row['nofinesset']),
            facility_name = str(row['facility_name']),
            region = row['comm_name'],
            coordinates = list(row['coords']), 
            resources_capacity = {"cap" : int(row['beds'] * 365)},
            max_transferable_in = {"cap": max_transferable_in},
            max_transferable_out = {"cap": max_transferable_out},
            linked_facilities = linked_facilities_dict[row['nofinesset']],
            available_pathways= _get_available_pathways(row["type"]))
    list_facilities = df_instance.apply(row_to_facility, axis=1).tolist()
    return list_facilities

def _get_available_pathways(f_type):
    """Returns available pathways for each facility ``type''"""
    pathways_dict = {"1": ["p1"], "2a": ["p1", "p2a"], "2b" :["p1", "p2a", "p2b"], "3": ["p1", "p2a", "p2b", "p3"]}
    return pathways_dict[f_type]


def get_Instance(df_instance : pd.DataFrame, list_pathways: list, list_groups, list_resources: list) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")    
    d_gr = get_demand_lower_bounds(df_instance)
    U_idx = list(set([k.quality_level for k in list_pathways]))

    return Instance(
            d_total = int(df_instance["deliveries_per_facility"].sum()),
            d_gr = d_gr,
            under_q_g = {p: config["min_fraction_to_be_treated"]  for p in  list_groups},
            over_q_g = {p: config["max_fraction_to_be_treated"]  for p in  list_groups},
            under_q_gu = {p: {u: config["min_fraction_to_be_treated"] for u in U_idx} for p in  list_groups},
            over_q_gu = {p: {u: config["max_fraction_to_be_treated"] for u in U_idx} for p in list_groups},
            p_transf = config["allowed_transfer_fraction"],
            delta_l = {l: config["resource_transfer_unit"] for l in list_resources},
            alpha = config["alpha"]
        )


def get_demand_lower_bounds(df_instance : pd.DataFrame) -> list[list[float]]:
    """ Returns ``d_gr'', the lower bound on patients asssigments per patient group, per commune
    extracted from ``summary_maternity_labours.csv'' and adjusted by maternity type"""
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    labour_types_distribution =  config["labour_types_distribution"]
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance["dep_code"])]
    df_labours = df_labours.drop(columns=["region_code"])
    df_comm_avg = (df_labours
        .groupby(["comm_code"], as_index=False)
        .agg(comm_deliveries=("deliveries_per_comm", "mean")))  
    
    d_gr = {}
    total_deliveries = df_comm_avg["comm_deliveries"].sum()
    for g, fraction in labour_types_distribution.items():
        d_gr[g] = { r: float((comm * fraction / total_deliveries))
                   for r, comm in zip(df_comm_avg["comm_code"], df_comm_avg["comm_deliveries"])}
    return d_gr


def get_Resources(list_resources: list) -> list[Resource]:
    """Creates Resource object with id for unique resource (bed/days)"""
    from backend.core.data_models.input_models import Resource
    return [Resource(resource_id=x) for x in list_resources]


def get_PatientGroups(groups_ids: list) -> list[PatientsGroup]:
    """Creates PatientGroups corresponding to French labour types status codes (1,2a,2b,3)"""
    list_patientsGroups = []
    possible_pathways = ["p" + g for g in groups_ids]
    for gid in groups_ids:
        list_patientsGroups.append(PatientsGroup(group_id= gid, possible_pathways= possible_pathways))
    return list_patientsGroups


def get_Activities(groups_ids: list) -> list[Activity]:
    """Creates Activity objects with required resources being the average length of stay for a labour in France in bed/days
    As a simplification the same average length of stay is currently used for all labour types
    """
    from backend.core.data_models.input_models import Activity
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    list_activities = [Activity(activity_id="a"+g, associated_pathway="p"+g,
                     associated_group=g, transferable=False,
                     transfer_to="", required_resources={"cap":config["avg_length_of_stay"]}) for g in groups_ids]
    return list_activities


def get_PatientPathways(groups_ids: list) -> list[Pathway]:
    """Creates Pathways objects for each patientGroup type"""
    pathways = [Pathway(pathway_id= "p"+g, associated_group_id = g, quality_level = "0", list_activities= [],
                         group_benefit = 1) for g in groups_ids]
    return pathways

    
def _get_affinities(df_instance: pd.DataFrame, df_geo_comms: gpd.GeoDataFrame):
    """ Returns {facility_id: {community_id: score}} where score is 1/Euclidian distance"""
    from shapely.geometry import Point
    import geopandas as gpd
    distances = np.zeros((len(df_instance), len(df_geo_comms)))
    facilities_points = gpd.GeoSeries([Point(c) for c in df_instance["coords"]], crs="EPSG:4326").to_crs(df_geo_comms.crs)
    for i, comm_geometry in enumerate(df_geo_comms.geometry):
        distances[:, i] = facilities_points.distance(comm_geometry)
    scores = 1 / np.where(distances == 0, 100, distances)
    affinities_dict = {comm_id: dict(zip(df_instance["nofinesset"].tolist(), scores[:, i])) \
                       for i, comm_id in enumerate(df_geo_comms["code"].tolist())}
    return affinities_dict


def serialize_maternite(df_instance : pd.DataFrame) -> Union[dict, dict]:
    """Serialize maternite objects into dictionaries (params_system.json; params_metadata.json)"""
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.data_models.input_models import SystemData
    groups_ids = ["1", "2a", "2b", "3"]
    resources_ids = ["cap"]

    list_regions = get_Regions(df_instance)
    list_facilities = get_Facilities(df_instance)
    list_resources = get_Resources(resources_ids)
    list_patients = get_PatientGroups(groups_ids)
    list_pathways = get_PatientPathways(groups_ids)
    list_activities = get_Activities(groups_ids)
    instance = get_Instance(df_instance, list_pathways, groups_ids, resources_ids)
    maternite_data = SystemData(regions = list_regions, resources=list_resources, facilities=list_facilities, patients=list_patients ,\
               pathways=list_pathways, activities= list_activities, instance=instance)
    params_system, params_metadata = convert_dm_to_json(maternite_data)
    return params_system, params_metadata



def read_maternity() -> pd.DataFrame:
    """Create Dataframe from summary_maternity_capacity.csv. We average the number of deliveries per facility across the years
    and take the latest number of beds recorded"""
    import ast 
    df = pd.read_csv("backend/data/open_data/summary_maternity_capacity.csv")
    df.loc[df["comm_code"] == "85166", "comm_code"] = "85194" # update the commune code of Olonne-sur-Mer
    df["coords"] = df["coords"].apply(ast.literal_eval)
    df.sort_values(by=["year"], ascending=False, inplace=True)
    df= (df.groupby(
        ["nofinesset","region_code", "region_name", "type", "dep_code",
         "dep_name", "comm_code", "facility_name", "comm_name", "coords"],
        as_index=False)
    .agg(deliveries_per_facility=("deliveries_per_facility", "mean"),
        beds=("beds", "first")))
    df = df.drop_duplicates(subset=["nofinesset"], keep="first")
    return df