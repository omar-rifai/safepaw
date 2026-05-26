
from typing import Tuple
import logging

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from backend.core.data_models.input_models import Facility, Pathway, PatientsGroup, CaseMixRatios, Instance
from backend.core.data_models.output_models import FacilityCapacity, DashboardStats
from sqlalchemy import func

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

def get_DashboardStats(session: Session) -> DashboardStats:
    from collections import defaultdict

    nbr_facilities = session.exec(select(func.count()).select_from(Facility)).one()
    nbr_pathways = session.exec(select(func.count()).select_from(Pathway)).one()
    nbr_groups = session.exec(select(func.count()).select_from(PatientsGroup)).one()
    case_mix = session.exec(select(CaseMixRatios)).all()
    instance = session.exec(select(Instance)).one()
    case_mix = [c.model_dump() for c in case_mix]
    stats = DashboardStats(nbr_facilities=nbr_facilities, nbr_pathways=nbr_pathways, nbr_patients_groups=nbr_groups, total_demand=instance.total_demand, case_mix=case_mix)
    return stats.model_dump() 


def update_instance(session: Session, new_instance):
    instance = session.exec(select(Instance)).one()
    print("new_instance",new_instance)
    for key, val in instance:
        setattr(instance, key, new_instance[key])
    session.commit()
    session.refresh(instance)

def get_facilities_capacities(session: Session, facility_ids: list | None = None) -> list[FacilityCapacity]:

    query = select(Facility).options(selectinload(Facility.facility_resources))
    if facility_ids:
        query = query.where(Facility.id.in_(facility_ids))
    facilities = session.exec(query).all()

    return [
        FacilityCapacity(
            facility_id=f.id,
            coordinates=[f.lat, f.lon],
            facility_type=f.facility_type,
            resources_capacity= f.resources_capacity if f.facility_resources else {})
        for f in facilities
    ]



def get_DataGridEntries(session: Session, facility_ids: list | None = None) -> dict:
    from backend.core.data_models.output_models import FacilityRow, FacilityPathwaysRow, FacilityGroupsRow, FacilityResourceRow, DataGridEntries
    from backend.core.data_models.input_models import Facility, Pathway, PatientsGroup, FacilityPathways, FacilityResources
    """Returns the data for the Datagrid components in frontend"""

    query_facilities = select(Facility)
    if facility_ids:
        query_facilities = query_facilities.where(Facility.id.in_(facility_ids))
    facilities = session.exec(query_facilities).all()

    query_pathways = select(Pathway, FacilityPathways.facility_id)\
        .join(FacilityPathways, FacilityPathways.pathway_id == Pathway.id)\
            .options(selectinload(Pathway.activities))
    if facility_ids:
        query_pathways = query_pathways.where(FacilityPathways.facility_id.in_(facility_ids)).distinct()
    pathways = session.exec(query_pathways).unique().all()
    pathways_entries = [FacilityPathwaysRow(facility_id= facility_id, pathway_id=p.id, group_id=p.group_id, quality_level=p.quality_level,
                                    group_benefit=p.group_benefit, activities=[a.id for a in p.activities]) for p, facility_id in pathways]

    query_resources = select(FacilityResources)
    if facility_ids:
        query_resources = query_resources.where(FacilityResources.facility_id.in_(facility_ids))
    resources = session.exec(query_resources).all()
    resources_entries = [FacilityResourceRow(facility_id = fr.facility_id, resource_id=fr.resource_id, capacity=fr.capacity) for fr in resources]
  
    query_groups = select(PatientsGroup, FacilityPathways.facility_id)\
        .join(Pathway, Pathway.group_id == PatientsGroup.id)\
            .join(FacilityPathways, FacilityPathways.pathway_id == Pathway.id)
    if facility_ids:
        query_groups = query_groups.where(FacilityPathways.facility_id.in_(facility_ids)).distinct()
    patients_groups =  session.exec(query_groups).unique().all()
    groups_entries = [FacilityGroupsRow(facility_id= facility_id, group_id=pg.id, lbl=pg.lbl, pathways=[p.id for p in pg.pathways]) for pg, facility_id in patients_groups]

    instance_entry = session.exec(select(Instance)).one()

    entry = DataGridEntries(
        facilities= [FacilityRow(facility_id=f.id, facility_name=f.name, facility_type=f.facility_type) for f in facilities],
        pathways= pathways_entries,
        resources= resources_entries,
        patients_groups= groups_entries,
        instance = instance_entry
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
