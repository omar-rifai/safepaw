
from typing import Tuple
import logging

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from backend.core.data_models.input_models import Facility
from backend.core.data_models.output_models import FacilityCapacity


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


def get_facilities_capacities(session: Session) -> list[FacilityCapacity]:
    return [
        FacilityCapacity(
            facility_id=f.id,
            coordinates=[f.lat, f.lon],
            facility_type=f.facility_type,
            resources_capacity= f.resources_capacity if f.facility_resources else {})
        for f in session.exec(select(Facility).options(selectinload(Facility.facility_resources))).all()
    ]



def get_DataGridEntries(session: Session) -> dict:
    from backend.core.data_models.output_models import FacilityRow,PathwayRow, PatientsGroupRow, ResourceRow, DataGridEntries
    from backend.core.data_models.input_models import Facility, Pathway, Resource, PatientsGroup

    facilities = session.exec(select(Facility)).all()
    pathways = session.exec(select(Pathway)).all()
    resources = session.exec(select(Resource)).all()
    patients_groups = session.exec(select(PatientsGroup)).all()
    entries = [DataGridEntries(
        facilities=[FacilityRow(facility_id=f.id, facility_name=f.name, facility_type=f.facility_type) for f in facilities],
        pathways=[PathwayRow(pathway_id=p.id, group_id=p.group_id, quality_level=p.quality_level, group_benefit=p.group_benefit, activities=[a.id for a in p.activities]) for p in pathways],
        resources=[ResourceRow(resource_id=r.id, transfer_unit=r.transfer_unit) for r in resources],
        patients_groups=[PatientsGroupRow(group_id=pg.id, lbl=pg.lbl, pathways=[p.id for p in pg.pathways]) for pg in patients_groups]
    )]
    return entries[0].model_dump() if entries else {}



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
