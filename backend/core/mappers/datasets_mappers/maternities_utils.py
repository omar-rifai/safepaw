import pandas as pd
import numpy as np
from backend.core.data_models.input_models import FacilityResources, FacilityPathways, LinkedFacilities, ActivityResources,\
    CaseMixRatios, TreatmentBounds, QualityBounds



def  get_FacilityAffinity(df_instance: pd.DataFrame, df_geo_comms: pd.DataFrame, dep_code: str,
                           osrm_distances_file="backend/data/open_data/distances_maternities.parquet"):
    from shapely.geometry import Point
    from shapely import distance
    import geopandas as gpd
    import numpy as np
    
    if dep_code:
        df_distances = pd.read_parquet(osrm_distances_file)
        df_distances = df_distances[df_distances["dep_code"] == dep_code]
        distances = df_distances.pivot(values="distance", index="nofinesset", columns="region").to_numpy()
        print("Using OSRM distance succesfully")
    else:    
        print(f"No department selected fallback to geodesic distance") 
        distances = np.zeros((len(df_instance), len(df_geo_comms)))
        facilities_points = gpd.GeoSeries([Point(c) for c in df_instance["coords"]], crs="EPSG:4326").to_crs(df_geo_comms.crs)
        facility_geoms = np.asarray(facilities_points.values)
        region_geoms = np.asarray(df_geo_comms.geometry.values)
        distances = distance(facility_geoms[:, None], region_geoms[None,:])

    scores = 1 / np.where(distances == 0, 100, distances)
    facility_ids = df_instance["nofinesset"].to_numpy()
    region_ids = df_geo_comms["code"].to_numpy()

    rows = [{"facility_id": facility_ids[i], "region_id": region_ids[j], "affinity_score": float(scores[i, j]),}
    for i in range(len(facility_ids))
    for j in range(len(region_ids))]

    return rows



def get_FacilityResources(df_instance: pd.DataFrame, max_transferable_in : int = 10, max_transferable_out : int = 1, RESOURCE_ID="bed/days"):
   return [FacilityResources(
        facility_id = str(row['nofinesset']),
        resource_id = RESOURCE_ID,
        capacity = int(row['beds'] * 365),
        max_transferable_in = max_transferable_in,
        max_transferable_out = max_transferable_out
    ) for _, row in df_instance.iterrows()]



def get_FacilityPathways(list_facilities):
    pathways_dict = {"1": ["p1"], "2a": ["p1", "p2a"], "2b" :["p1", "p2a", "p2b"], "3": ["p1", "p2a", "p2b", "p3"]}
    return [FacilityPathways(facility_id=f.id, group_id=f.facility_type, pathway_id=p) for f in list_facilities for p in pathways_dict[f.facility_type]]


def get_LinkedFacilities(list_facilities):
    return [LinkedFacilities(facility_id=f.id, linked_facility_id=lf.id) for f in list_facilities for lf in list_facilities if f.id != lf.id]

def get_ActivityResources():
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    required_resources={"bed/days":config["avg_length_of_stay"]}
    return [ActivityResources(activity_id="accouchement_"+g, pathway_id= "p"+g, group_id=g, resource_id=r, required_capacity=cap) for g in ["1", "2a", "2b", "3"]
            for r, cap in required_resources.items()]



def get_CaseMixRatios(df_instance: pd.DataFrame):
    """Returns the lower bound on patients asssigments per patient group, per commune"""
    from backend.core.mappers.datasets_mappers.maternities_serializer import DF_LABOURS_ALL
    from backend.core.utils.data_utils import read_configs

    config = read_configs("data_maternity")
    labour_types_distribution =  config["labour_types_distribution"]
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance.apply(lambda x: x["dep_code"], axis=1))]
    df_labours = df_labours.drop(columns=["region_code"])
    df_comm_avg = (df_labours
        .groupby(["comm_code"], as_index=False)
        .agg(comm_deliveries=("deliveries_per_comm", "mean")))  
    
    d_gr = {}
    total_deliveries = df_comm_avg["comm_deliveries"].sum()
    for g, fraction in labour_types_distribution.items():
        d_gr[g] = { r: float((comm * fraction / total_deliveries))
                   for r, comm in zip(df_comm_avg["comm_code"], df_comm_avg["comm_deliveries"])}

    return [CaseMixRatios(group_id=g, region_id=r, ratio=ratio) for g, comm_ratios in d_gr.items() for r, ratio in comm_ratios.items()]

def get_TreatmentBounds(list_groups: list):
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")    
    return [TreatmentBounds(group_id=g.id, min_treatment_bound=config["min_fraction_to_be_treated"] ,
                             max_treatment_bound=config["max_fraction_to_be_treated"]) for g in list_groups]


def get_QualityBounds(list_groups: list, list_qualities: list):
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")    
    return [QualityBounds(group_id=g.id, quality_id=u, min_quality_bound=config["min_quality_bound"], max_quality_bound=config["max_quality_bound"]) 
            for g in list_groups for u in list_qualities]
