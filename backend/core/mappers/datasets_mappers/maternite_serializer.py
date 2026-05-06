import pandas as pd
from typing import Union
from backend.core.data_models.input_models import Facility, Region, Instance, Resource, PatientsGroup, Activity, Pathway
import geopandas as gpd
import numpy as np
import typer

FACILITY_TYPES = ["1", "2a", "2b", "3"]
RESOURCES_IDS = ["cap"]
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


def pad_single(dep_code: str):
    if not dep_code.isdigit():
        raise("Unhandled department code number", dep_code)
    if int(dep_code) < 10 and len(dep_code) == 1:
        return "0" + dep_code
    return dep_code


def get_Regions(df_instance: pd.DataFrame) -> list[Region]:
    """Creates `Region` instance using public data on French communes (Commune code and coordinates)"""
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance.apply(lambda x: x["region_id"][:2], axis=1))]
    df_geo_comms = DF_GEO_COMMS_METERS[DF_GEO_COMMS_METERS["code"].isin(df_labours["comm_code"])]
    affinities_dict = _get_affinities(df_instance, df_geo_comms)
    list_regions = []
    for _, row in df_geo_comms.iterrows():
        list_regions.append(Region(region_id=row["code"],
                                   coordinates=DICT_COMM_CENTROIDS[row["code"]],
                                   facilities_affinity=affinities_dict[row["code"]],
                                   dep_code=row["departement"],
                                   comm_code=row["code"],
                                   region_lbl=row["nom"]
                                   ))
    
    return list_regions


def get_Facilities(region_code: str = None, dep_code :str = None,
                   max_transferable_in : int = 10, max_transferable_out : int = 1) -> list[Facility]:
    """
    Creates Facility objects corresponding to unique nofinesset ids with (bed/days) as resource 
    and availiable pathways dependent on to the facility type (1,2a,2b,3). We average the number of deliveries
    per facility across the yearsand take the latest number of beds recorded
    """
    import ast 
        
    df_instance = pd.read_csv("backend/data/open_data/summary_maternity_capacity.csv")
    df_instance.loc[df_instance["comm_code"] == "85166", "comm_code"] = "85194" # update the commune code of Olonne-sur-Mer
    df_instance["coords"] = df_instance["coords"].apply(ast.literal_eval)
    df_instance.sort_values(by=["year"], ascending=False, inplace=True)
    if region_code: 
        df_instance = df_instance[df_instance["region_code"].astype(str) == str(region_code)]
    if dep_code: df_instance = df_instance[df_instance["dep_code"] == pad_single(dep_code)]
    df_instance = (df_instance.groupby(
        ["nofinesset","region_code", "region_name", "type", "dep_code",
         "dep_name", "comm_code", "facility_name", "comm_name", "coords"],
        as_index=False)
    .agg(deliveries_per_facility=("deliveries_per_facility", "mean"),
        beds=("beds", "first")))
    df_instance = df_instance.drop_duplicates(subset=["nofinesset"], keep="first")

    all_ids = df_instance["nofinesset"].sort_values().to_list()
    linked_facilities_dict = {fid: [x for x in all_ids if x != fid] for fid in all_ids} 
    def row_to_facility(row):
        return Facility(
            facility_id = str(row['nofinesset']),
            facility_name = str(row['facility_name']),
            facility_type = str(row["type"]),
            region_id = row['comm_code'],
            coordinates = list(row['coords']),
            nbr_visits= row["deliveries_per_facility"],
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
            d_total = int(df_instance["nbr_visits"].sum()),
            d_gr = d_gr,
            under_q_g = {p: config["min_fraction_to_be_treated"]  for p in  list_groups},
            over_q_g = {p: config["max_fraction_to_be_treated"]  for p in  list_groups},
            under_q_gu = {p: {u: config["min_fraction_to_be_treated"] for u in U_idx} for p in  list_groups},
            over_q_gu = {p: {u: config["max_fraction_to_be_treated"] for u in U_idx} for p in list_groups},
            p_transf = config["allowed_transfer_fraction"],
            delta_l = {l: config["resource_transfer_unit"] for l in list_resources},
            alpha = config["alpha"],
            mode= "maternity"
        )


def get_demand_lower_bounds(df_instance : pd.DataFrame) -> list[list[float]]:
    """ Returns ``d_gr'', the lower bound on patients asssigments per patient group, per commune
    extracted from ``summary_maternity_labours.csv'' and adjusted by maternity type"""
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    labour_types_distribution =  config["labour_types_distribution"]
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance.apply(lambda x: x["region_id"][:2], axis=1))]
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
    facilities_points = gpd.GeoSeries([Point(c) for c in df_instance["coordinates"]], crs="EPSG:4326").to_crs(df_geo_comms.crs)
    for i, comm_geometry in enumerate(df_geo_comms.geometry):
        distances[:, i] = facilities_points.distance(comm_geometry)
    scores = 1 / np.where(distances == 0, 100, distances)
    affinities_dict = {comm_id: dict(zip(df_instance["facility_id"].tolist(), scores[:, i])) \
                       for i, comm_id in enumerate(df_geo_comms["code"].tolist())}
    return affinities_dict


def serialize_maternity_core(df_instance : pd.DataFrame, save_params: bool = False) -> Union[dict, dict]:
    """Serialize maternite objects into dictionaries (params_system.json; params_metadata.json)"""
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.data_models.input_models import SystemData
    import json, os

    list_regions = get_Regions(df_instance)
    list_facilities = [Facility.model_validate(x) for x in df_instance.to_dict(orient="records")]
    list_resources = get_Resources(RESOURCES_IDS)
    list_patients = get_PatientGroups(FACILITY_TYPES)
    list_pathways = get_PatientPathways(FACILITY_TYPES)
    list_activities = get_Activities(FACILITY_TYPES)
    instance = get_Instance(df_instance, list_pathways, FACILITY_TYPES, RESOURCES_IDS)
    maternite_data = SystemData(regions = list_regions, resources=list_resources, facilities=list_facilities, patients=list_patients ,\
               pathways=list_pathways, activities= list_activities, instance=instance)
    params_system  = convert_dm_to_json(maternite_data)
    if save_params :
        os.makedirs("experiments", exist_ok=True)
        with open("experiments/params_maternity.json", "w") as fp:
            json.dump(params_system, fp)
    return params_system



def serialize_maternity(
        region_code: str = typer.Option(None, help="French region code (as string)"),
        dep_code: str = typer.Option(None, help="French department code (as string)"),
        save_params: bool = typer.Option(True)
        ):
    df_instance = pd.DataFrame([x.model_dump(mode="python") for x in get_Facilities(region_code= region_code, dep_code= dep_code)])
    return serialize_maternity_core(df_instance, save_params)


if __name__ == "__main__":
     typer.run(serialize_maternity)