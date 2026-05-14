
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


def get_bounding_box(session):
    from shapely.geometry import box, mapping

    xs = session.exec(select(Facility.lat)).all()
    ys = session.exec(select(Facility.lon)).all()

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


def get_facilities_capacities(session: Session, facility_id: str | None = None) -> list[FacilityCapacity]:

    query = select(Facility).options(selectinload(Facility.facility_resources))
    if facility_id is not None:
        query = query.where(Facility.id == facility_id)
    facilities = session.exec(query).all()

    return [
        FacilityCapacity(
            facility_id=f.id,
            coordinates=[f.lat, f.lon],
            facility_type=f.facility_type,
            resources_capacity= f.resources_capacity if f.facility_resources else {})
        for f in facilities
    ]



def get_DataGridEntries(session: Session, facility_id: str | None = None) -> dict:
    from backend.core.data_models.output_models import FacilityRow,PathwayRow, PatientsGroupRow, ResourceRow, DataGridEntries
    from backend.core.data_models.input_models import Facility, Pathway, Resource, PatientsGroup, FacilityPathways, FacilityResources
    
    query_facilities = select(Facility)
    if facility_id is not None:
        query_facilities = query_facilities.where(Facility.id == facility_id)
    facilities = session.exec(query_facilities).all()

    query_pathways = select(Pathway).options(selectinload(Pathway.activities))
    if facility_id is not None:
        query_pathways = query_pathways.join(FacilityPathways).where(FacilityPathways.facility_id == facility_id).distinct()
    pathways = session.exec(query_pathways).all()

    query_resources = select(Resource)
    if facility_id is not None:
        query_resources = select(Resource, FacilityResources)
        query_resources = query_resources.join(FacilityResources).where(FacilityResources.facility_id == facility_id)
    resources = session.exec(query_resources).all()
    
    if facility_id is not None: 
        resources_entries = [ResourceRow(resource_id=r.id, transfer_unit=r.transfer_unit, capacity=fr.capacity) for r, fr in resources]
    else: 
        resources_entries = [ResourceRow(resource_id=r.id, transfer_unit=r.transfer_unit) for r in resources]

    query_groups = select(PatientsGroup)
    if facility_id is not None:
        query_groups = query_groups\
            .join(Pathway, Pathway.group_id == PatientsGroup.id)\
            .join(FacilityPathways).where(FacilityPathways.facility_id == facility_id).distinct()
    patients_groups =  session.exec(query_groups).all()

    entry = DataGridEntries(
        facilities=[FacilityRow(facility_id=f.id, facility_name=f.name, facility_type=f.facility_type) for f in facilities],
        pathways=[PathwayRow(pathway_id=p.id, group_id=p.group_id, quality_level=p.quality_level, group_benefit=p.group_benefit, activities=[a.id for a in p.activities]) for p in pathways],
        resources=resources_entries,
        patients_groups=[PatientsGroupRow(group_id=pg.id, lbl=pg.lbl, pathways=[p.id for p in pg.pathways]) for pg in patients_groups]
    )


    return entry.model_dump() if entry else {}



def clear_all_tables(session):
    from sqlmodel import text, SQLModel
    session.exec(text("PRAGMA foreign_keys=OFF"))  # SQLite only

    for table in reversed(SQLModel.metadata.sorted_tables):
        session.exec(text(f"DELETE FROM {table.name}"))

    session.commit()




def run_optimization(params: dict) -> Tuple[str, str, list, dict]:
    """Returns status, objective function as str and a dict of result variables"""
    from backend.core.main import run_driver
    check_executable()
    print("Starting optimization driver...")
    status, objective, results = run_driver(params)
    print("Optimization driver finished with status:", status)
    objective_str = f"{objective:.2f}" if objective is not None else None
    return status, objective_str, results
