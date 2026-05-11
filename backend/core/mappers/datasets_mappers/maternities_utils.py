import pandas as pd
import numpy as np
from backend.core.data_models.input_models import FacilityAffinity, FacilityResources, FacilityPathways, LinkedFacilities, ActivityResources,\
    CaseMixRatios, TreatmentBounds, QualityBounds



def  get_FacilityAffinity(df_instance: pd.DataFrame, df_geo_comms: pd.DataFrame):
    from shapely.geometry import Point
    import geopandas as gpd
    distances = np.zeros((len(df_instance), len(df_geo_comms)))
    facilities_points = gpd.GeoSeries([Point(c) for c in df_instance["coords"]], crs="EPSG:4326").to_crs(df_geo_comms.crs)
    for i, comm_geometry in enumerate(df_geo_comms.geometry):
        distances[:, i] = facilities_points.distance(comm_geometry)
    scores = 1 / np.where(distances == 0, 100, distances)
    affinities_dict = {comm_id: dict(zip(df_instance["nofinesset"].tolist(), scores[:, i])) \
                       for i, comm_id in enumerate(df_geo_comms["code"].tolist())}
    
    return [FacilityAffinity(facility_id=facility_id, region_id=comm_id, affinity_score=score)
            for comm_id, facility_scores in affinities_dict.items()
            for facility_id, score in facility_scores.items()]


def get_FacilityResources(df_instance: pd.DataFrame, max_transferable_in : int = 10, max_transferable_out : int = 1, RESOURCE_ID="cap"):
   return [FacilityResources(
        facility_id = str(row['nofinesset']),
        resource_id = RESOURCE_ID,
        capacity = int(row['beds'] * 365),
        max_transferable_in = max_transferable_in,
        max_transferable_out = max_transferable_out
    ) for _, row in df_instance.iterrows()]



def get_FacilityPathways(list_facilities):
    pathways_dict = {"1": ["p1"], "2a": ["p1", "p2a"], "2b" :["p1", "p2a", "p2b"], "3": ["p1", "p2a", "p2b", "p3"]}
    return [FacilityPathways(facility_id=f.id, pathway_id=p) for f in list_facilities for p in pathways_dict[f.facility_type]]


def get_LinkedFacilities(list_facilities):
    return [LinkedFacilities(facility_id=f.id, linked_facility_id=lf.id) for f in list_facilities for lf in list_facilities]

def get_ActivityResources():
    from backend.core.utils.data_utils import read_configs
    config = read_configs("data_maternity")
    required_resources={"cap":config["avg_length_of_stay"]}
    return [ActivityResources(activity_id="a"+g, resource_id=r, required_capacity=cap) for g in ["1", "2a", "2b", "3"]
            for r, cap in required_resources.items()]



def get_CaseMixRatios(df_instance: pd.DataFrame):
    """Returns the lower bound on patients asssigments per patient group, per commune"""
    from backend.core.mappers.datasets_mappers.maternities_serializer import DF_LABOURS_ALL
    from backend.core.utils.data_utils import read_configs

    config = read_configs("data_maternity")
    labour_types_distribution =  config["labour_types_distribution"]
    df_labours = DF_LABOURS_ALL[DF_LABOURS_ALL["dep_code"].isin(df_instance.apply(lambda x: x["region_code"], axis=1))]
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
