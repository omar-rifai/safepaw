from pathlib import Path
from typing import Tuple
from backend.core.mappers.output_mappers import create_facilityStats
import pandas as pd 
import logging
logging.basicConfig(level=logging.DEBUG)


def get_department_code(dep_name: str) -> str:
    df_departments = pd.read_csv("backend/data/open_data/departments.csv")
    dep_code = str(df_departments[df_departments["name"]==dep_name]["code"].iloc[0])
    return dep_code

def get_region_code(region_name: str)-> str:
    df_regions = pd.read_csv("backend/data/open_data/regions.csv")
    print("here", region_name)
    print(df_regions["nom_region"].unique())
    region_code = str(df_regions[df_regions["nom_region"]==region_name]["code_region"].iloc[0])
    return region_code


class ExecutableNotFound(Exception):
    pass


def check_executable():
    #TODO: check for gurobi or HiGHS
    return True

def run_optimization_maternite(df_instance : pd.DataFrame, transfers : float) -> Tuple[str, str, list, list]:
    """Run the optimization problem with a the upper bound of allowed resource export set to `transfers`"""
    from backend.core.mappers.datasets_mappers.maternite_serializer import serialize_maternity_core
    from backend.core.mappers.output_mappers import get_average_distance
    from backend.core.main import run_driver
    check_executable()
    params_system = serialize_maternity_core(df_instance)
    params_system["b_hl_out"] = {h : {"cap": transfers} for h in params_system["H"]}
    print("Starting optimization driver...")
    status, objective, results = run_driver(params_system, mode="maternity")
    print("Optimization driver finished with status:", status)
    if objective is None:
        return status, None, [], [], []
    else:
        list_facility_load = create_facilityStats(results, params_system) if objective is not None else []
        list_facility_load_regions = create_facilityStats(results, params_system, by_region=True) if objective is not None else [] 
        average_distance = get_average_distance(results, params_system)
    return status, average_distance, [], list_facility_load, list_facility_load_regions, list(params_system["regions_metadata"].keys())



def run_optimization(params: dict) -> Tuple[str, str, list, dict]:
    """Returns status, objective function as str and a dict of result variables"""
    from backend.core.main import run_driver
    check_executable()
    print("Starting optimization driver...")
    status, objective, results = run_driver(params)
    print("Optimization driver finished with status:", status)
    objective_str = f"{objective:.2f}" if objective is not None else None
    return status, objective_str, results


def get_regions_metadata(metadata_filepath: str | Path)-> dict:
    from backend.core.utils import data_utils
    params_metadata = data_utils.read_metadata(metadata_filepath)
    return params_metadata["regions"]



def get_maternite_dashboard(df_maternites):

    dashboard_stats = {}

    #nbr accouchements moyen par année 
    avg_births_year = df_maternites["nbr_visits"].mean()
    dashboard_stats["Average yearly births / facility"] = round(avg_births_year)

    #nbr accouchements moyen par lit / année
    avg_births_bed = (df_maternites["nbr_visits"] / [x["cap"]/365 for x in df_maternites["resources_capacity"]]).mean()
    dashboard_stats["Average yearly births / bed"] =  round(avg_births_bed)

   
    return dashboard_stats


def get_facility_capacity(df) -> list:
    """ Returns a list of FacilityStats Instances """
    from backend.core.data_models.output_models import FacilityStats
    list_facilities_capacity = []
    for _, h in df.iterrows():
        facility_instance = FacilityStats(
            facility_id = h["facility_id"],
            facility_name = h["facility_name"],
            facility_type = h["facility_type"],
            coordinates = h["coordinates"],
            patient_group = None,
            patient_pathway = None,
            region_id = None,
            capacities = h["resources_capacity"])
        list_facilities_capacity.append(facility_instance)
    return [pt.as_geojson_feature() for pt in list_facilities_capacity]