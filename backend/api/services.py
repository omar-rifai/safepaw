from pathlib import Path
from typing import Tuple
from backend.core.mappers.output_mappers import create_facilityStats, create_patientTransfers
import pandas as pd 
import logging
logging.basicConfig(level=logging.DEBUG)


class ExecutableNotFound(Exception):
    pass


def check_executable(exec_name="highs"):
    import shutil

    solver_path = shutil.which(exec_name)
    print("Solver path:", solver_path)
    if solver_path is None:
        raise ExecutableNotFound(f"Executable '{exec_name}' not found")

def run_optimization_maternite(df_instance : pd.DataFrame, transfers : float) -> Tuple[str, str, list, list]:
    """Run the optimization problem with a the upper bound of allowed resource export set to `transfers`"""
    from backend.core.mappers.datasets_mappers.maternite_serializer import serialize_maternite
    from backend.core.main import run_driver
    check_executable() # Check solver
    params_system, params_metadata = serialize_maternite(df_instance)
    params_system["b_hl_out"] = [[transfers] for _ in range(len(params_system["H"]))]
    print("Starting optimization driver...")
    status, objective, results = run_driver(params_system)
    print("Optimization driver finished with status:", status)
    if objective is None:
        return status, "N/A", [], [], [], params_metadata["regions"]
    else:
        list_patient_transfers = create_patientTransfers(results, params_system, params_metadata) if objective is not None else []
        list_facility_load = create_facilityStats(results, params_system, params_metadata) if objective is not None else []
        list_facility_load_regions = create_facilityStats(results, params_system, params_metadata, by_region=True) if objective is not None else []
    return status, f"{objective:.2f}", list_patient_transfers, list_facility_load, list_facility_load_regions, params_metadata["regions"]



def run_optimization(params_filepath: str | Path, metadata_filepath: str | Path) -> Tuple[str, str, list, list]:
    from backend.core.utils import data_utils
    from backend.core.main import run_driver

    # Check solver
    check_executable()

    # Load input
    params_system = data_utils.read_inputs(params_filepath)
    params_metadata = data_utils.read_metadata(metadata_filepath)

    # Run optimization
    print("Starting optimization driver...")
    status, objective, results = run_driver(params_system)
    print("Optimization driver finished with status:", status)

    # Format output
    objective_str = f"{objective:.2f}" if objective is not None else "N/A"
    
    list_patient_transfers = create_patientTransfers(results, params_system, params_metadata)
    list_facility_load = create_facilityStats(results, params_system, params_metadata)
    list_facility_load_regions = create_facilityStats(results, params_system, params_metadata, by_region=True)
    

    return status, objective_str, list_patient_transfers, list_facility_load, list_facility_load_regions


def get_regions_metadata(metadata_filepath: str | Path)-> dict:
    from backend.core.utils import data_utils
    params_metadata = data_utils.read_metadata(metadata_filepath)
    return params_metadata["regions"]



def get_maternite_dashboard(df_maternites):

    dashboard_stats = {}

    #nbr accouchements moyen par année 
    avg_births_year = df_maternites["deliveries_per_facility"].mean()
    dashboard_stats["Avg births / facility"] = round(avg_births_year)

    #nbr accouchements moyen par lit / année
    avg_births_bed = (df_maternites["deliveries_per_facility"] / df_maternites["beds"]).mean()
    dashboard_stats["Avg birth / bed"] =  round(avg_births_bed)

   
    return dashboard_stats


def get_facility_capacity_maternite(df_maternites) -> list:
    """ Returns a list of FacilityStats Instances """
    from backend.core.data_models.output_models import FacilityStats

    list_facilities_capacity = []

    for h in df_maternites["facility_name"].unique():
        
        beds_capacity = int(df_maternites.loc[df_maternites["facility_name"] == h, "beds"].iloc[0])
        coords = df_maternites.loc[df_maternites["facility_name"] == h,"coords"].iloc[0]
        facility_type = df_maternites.loc[df_maternites["facility_name"] == h,"type"].iloc[0]

        facility_instance = FacilityStats(
            facility_id=h,
            facility_type=facility_type,
            coordinates=coords,
            patient_group=None,
            patient_pathway=None,
            region_id=None,
            capacities={"beds": beds_capacity}
        )

        list_facilities_capacity.append(facility_instance)
    
    return [pt.as_geojson_feature() for pt in list_facilities_capacity]