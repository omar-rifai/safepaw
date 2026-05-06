
from typing import Tuple
import logging
from backend.core.data_models.input_models import Facility


logging.basicConfig(level=logging.DEBUG)


class ExecutableNotFound(Exception):
    pass


def check_executable():
    #TODO: check for gurobi or HiGHS
    return True


def get_bounding_box(params: dict):
    from shapely.geometry import box, mapping
    coords = []
    for h in params["facilities_metadata"]:
        coords.append(params["facilities_metadata"][h]["coords"])

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    bbox = box(min(xs), min(ys), max(xs), max(ys))
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(bbox),
                "properties": {}
            }
        ]
    }


def unify_updated_facility(mode, updated: dict) -> dict:
    from backend.core.mappers.datasets_mappers.maternite_serializer import _get_available_pathways
    if mode == "maternity":
        new_dict = {**updated, "resources_capacity":updated["resources_capacity"],
                     "available_pathways":_get_available_pathways(updated["facility_type"])}
    else:
        new_dict = updated
    return new_dict

def run_optimization(params: dict, mode:str="default") -> Tuple[str, str, list, dict]:
    """Returns status, objective function as str and a dict of result variables"""
    from backend.core.main import run_driver
    check_executable()
    print("Starting optimization driver...")
    status, objective, results = run_driver(params, mode)
    print("Optimization driver finished with status:", status)
    objective_str = f"{objective:.2f}" if objective is not None else None
    return status, objective_str, results
