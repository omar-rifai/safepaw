import pandas as pd
from typing import Union
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
from backend.core.utils.data_utils import read_geojson_projected


def get_Regions(df_instance: pd.DataFrame) -> list[Region]:
    """Creates `Region` instance using public data on French communes (Commune code and coordinates)"""
    import numpy as np
    df_labours = pd.read_csv("backend/data/open_data/summary_maternity_labours.csv", low_memory=False)
    df_labours = df_labours[df_labours["dep_code"].isin(df_instance["dep_code"])]
    df_geo_comms = read_geojson_projected("backend/data/open_data/communes-50m.geojson")
    df_geo_comms_4326 = df_geo_comms.to_crs(epsg=4326)
    dict_comm_centroids = dict(zip(df_geo_comms_4326["code"], np.vstack([df_geo_comms_4326.geometry.centroid.x.values, df_geo_comms_4326.geometry.centroid.y.values]).T))
    df_geo_comms = df_geo_comms[df_geo_comms["code"].isin(df_labours["comm_code"])]
    communes_ids = list(df_geo_comms["code"].drop_duplicates().sort_values())
    list_regions = [Region(region_id=c_id, coordinates=dict_comm_centroids[c_id], facilities_affinity=_get_affinities(c_id, df_instance, df_geo_comms)) for c_id in communes_ids]
    return list_regions

def get_Facilities(df_instance : pd.DataFrame, max_transferable_in : int = 10, max_transferable_out : int = 1) -> list[Facility]:
    """Creates Facility objects corresponding to unique nofinesset ids with (bed/days) as resource 
    and availiable pathways dependent on to the facility type (1,2a,2b,3)
    """
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
    pathways_dict = {"1": ["p1"], "2a": ["p1", "p2a"], "2b" :["p1", "p2b"], "3": ["p1", "p2a", "p2b", "p3"]}
    return pathways_dict[f_type]


def get_Instance(df_instance : pd.DataFrame) -> Instance:
    """Returns object to store optimization instance parameters. Most variables are stores in a global config.yaml file """
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")    
    d_gr = get_demand_lower_bounds(df_instance)
    n_g = len(d_gr)
    return Instance(
            d_total = int(df_instance["deliveries_per_facility"].sum()),
            d_gr = d_gr,
            under_q_g = [config["min_fraction_to_be_treated"] for i in range(n_g)],
            over_q_g = [config["max_fraction_to_be_treated"] for i in range(n_g)],
            under_q_gu = [[config["min_fraction_to_be_treated"]]*n_g],
            over_q_gu = [[config["max_fraction_to_be_treated"]]*n_g],
            p_transf = config["allowed_transfer_fraction"],
            delta_l = [config["resource_transfer_unit"]],
            alpha = config["alpha"]
        )


def get_demand_lower_bounds(df_instance : pd.DataFrame) -> list[list[float]]:
    """ Returns ``d_gr'', the lower bound on patients asssigments per patient group, per commune
    extracted from ``summary_maternity_labours.csv'' and adjusted by maternity type"""
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    labour_types_distribution =  config["labour_types_distribution"]
    df_labours = pd.read_csv("backend/data/open_data/summary_maternity_labours.csv", low_memory=False)
    df_labours = df_labours[df_labours["dep_code"].isin(df_instance["dep_code"])]
    df_labours = df_labours.drop(columns=["region_code"])
    df_comm_avg = (df_labours
        .groupby(["comm_code"], as_index=False)
        .agg(comm_deliveries=("deliveries_per_comm", "mean")))  
    d_gr = [(df_comm_avg["comm_deliveries"] * f / (df_comm_avg["comm_deliveries"]).sum()).tolist()
    for f in labour_types_distribution.values()]
    return d_gr


def get_Resources(df_instance : pd.DataFrame) -> list[Resource]:
    """Creates Resource object with id for unique resource (bed/days)"""
    from backend.core.data_models.input_models import Resource
    return [Resource(resource_id="l0")]


def get_PatientGroups(df_instance: pd.DataFrame) -> list[PatientsGroup]:
    """Creates PatientGroups corresponding to French labour types status codes (1,2a,2b,3)"""
    list_patientsGroups = []
    group_ids = ["1", "2a", "2b", "3"]
    possible_pathways = ["p" + g for g in group_ids]
    for gid in group_ids:
        list_patientsGroups.append(PatientsGroup(group_id= gid, possible_pathways= possible_pathways))
    return list_patientsGroups


def get_Activities(df_instance : pd.DataFrame) -> list[Activity]:
    """Creates Activity objects with required resources being the average length of stay for a labour in France in bed/days
    As a simplification the same average length of stay is currently used for all labour types
    """
    from backend.core.data_models.input_models import Activity
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    group_ids = ["1", "2a", "2b", "3"]
    list_activities = [Activity(activity_id="a"+g, associated_pathway="p"+g,
                     associated_group=g, transferable=False,
                     transfer_to="", required_resources={"l0":config["avg_length_of_stay"]}) for g in group_ids]
    return list_activities


def get_PatientPathways(df_instance : pd.DataFrame) -> list[Pathway]:
    """Creates Pathways objects for each patientGroup type"""
    group_ids = ["1", "2a", "2b", "3"]
    pathways = [Pathway(pathway_id= "p"+g, associated_group_id = g, quality_level = "0", list_activities= [],
                         group_benefit = 1, list_next = []) for g in group_ids]
    return pathways

    
def _get_affinities(c_id: str, df_instance: pd.DataFrame, geo_comms):
    """Calculates scores linking facilities (nofinesset) to regions (french departments) based on distance
    for the department the facility is in, score = 10 (high preference)
    """
    from shapely.geometry import Point
    import geopandas as gpd
    comm_geom = geo_comms.loc[geo_comms["code"] == c_id, "geometry"].iloc[0]
    gdf_points = gpd.GeoSeries([Point(c) for c in df_instance["coords"]], crs="EPSG:4326").to_crs(geo_comms.crs)  
    distances = gdf_points.distance(comm_geom)
    distances[distances == 0] = 100
    df_facilities = df_instance[["nofinesset"]].reset_index(drop=True).copy()
    df_facilities["score"] = 1 / distances
    return dict(zip(df_facilities["nofinesset"], df_facilities["score"]))


def serialize_maternite(df_instance : pd.DataFrame) -> Union[dict, dict]:
    """Serialize maternite objects into dictionaries (params_system.json; params_metadata.json)"""
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.data_models.input_models import SystemData
    list_regions = get_Regions(df_instance)
    list_facilities = get_Facilities(df_instance)
    maternite_data = SystemData(regions = list_regions, resources=get_Resources(df_instance), facilities= list_facilities, patients= get_PatientGroups(df_instance),\
               pathways=get_PatientPathways(df_instance), activities= get_Activities(df_instance), instance=get_Instance(df_instance))
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