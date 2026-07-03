
from typing import Tuple
import logging
from redis import Redis
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from backend.core.data_models.jobs_model import Job
from backend.core.data_models.input_models import Facility, Pathway, PatientsGroup, CaseMixRatios, Instance, Region, FacilityResources
from backend.core.data_models.output_models import FacilityCapacity, InstanceData
from sqlalchemy import func
from rq import Queue


logging.basicConfig(level=logging.DEBUG)
redis = Redis(host="localhost", port=6379)

class ExecutableNotFound(Exception):
    pass


def check_executable():
    #TODO: check for gurobi or HiGHS
    return True


def get_bounding_box(session):
    from shapely.geometry import box, mapping

    xs = session.exec(select(Facility.lon)).all()
    ys = session.exec(select(Facility.lat)).all()

    if not xs or not ys:
        bbox = box(-5.2, 41.3, 9.7, 51.1)  # Metropolitan France
    else:
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

def get_InstanceData(session: Session) -> InstanceData:

    nbr_facilities = session.exec(select(func.count()).select_from(Facility)).one()
    nbr_pathways = session.exec(select(func.count()).select_from(Pathway)).one()
    nbr_groups = session.exec(select(func.count()).select_from(PatientsGroup)).one()
    case_mix = session.exec(select(CaseMixRatios)).all()
    instance = session.exec(select(Instance)).one_or_none()
    case_mix = [c.model_dump() for c in case_mix]
    if instance:
        instance_data = InstanceData(instance_mode =instance.id, dep_code=instance.dep_code, nbr_facilities=nbr_facilities, nbr_pathways=nbr_pathways, nbr_patients_groups=nbr_groups, total_demand=int(instance.total_demand), case_mix=case_mix)
    return instance_data.model_dump() if instance else {}


def create_job_db_entry(session: Session, job_id:str, mode, dep_code):
    try:
        print(f"Creating job {mode} in {dep_code}")
        curr_job = Job(id=job_id, status="Running", mode=mode, dep_code=dep_code)
        session.add(curr_job)
        session.commit()
        session.refresh(curr_job)
    except Exception:
        print("Exception in job creation...")
        session.rollback()
        raise
    return 

def update_job_status(session: Session, job_id: str, new_status:str):
    try:
        job = session.exec(select(Job).where(Job.id == job_id)).one()
        setattr(job, "status", new_status)
        session.add(job)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return


def update_job_optid(session: Session, job_id: str, opt_id:str):
    try:
        job = session.exec(select(Job).where(Job.id == job_id)).one()
        setattr(job, "opt_id",opt_id)
        session.add(job)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return


def update_instance(session: Session, new_instance):
    instance = session.exec(select(Instance)).one()
    facility_resources = session.exec(select(FacilityResources)).all()
    for key, _ in instance: 
        setattr(instance, key, new_instance[key])
        if key == "global_multiplier_transfers":
            for fr in facility_resources:
                setattr(fr, "max_transferable_out", new_instance["global_multiplier_transfers"])
                if new_instance["global_multiplier_transfers"] > 0:
                    setattr(fr, "max_transferable_in", 10)
                else:
                    setattr(fr, "max_transferable_in", 0)
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


def save_instance_into_db(params:dict , session: Session):
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json
    clear_all_tables(session)
    convert_dm_from_json(params, session)
    session.commit()
    return 

def get_input_elements(session: Session, queue: Queue) -> dict:
    facilities_capacities = get_facilities_capacities(session)
    data_grid_entries = get_DataGridEntries(session)
    instance_data = get_InstanceData(session)
    jobs_list = getJobs(session, queue)
    return { "facilities_capacities":[f.model_dump() for f in facilities_capacities],
             "entries": data_grid_entries,
             "instance_data": instance_data,
             "bbox": get_bounding_box(session),
             "jobs": [j.model_dump(mode="json") for j in jobs_list]
            }

def getJobs(session:Session, queue: Queue):
    from rq.registry import FailedJobRegistry,CanceledJobRegistry

    canceled_registry = CanceledJobRegistry(queue=queue)
    failed_registry =FailedJobRegistry(queue=queue)
    jobs_list = session.exec(select(Job)).all()
    for job in jobs_list:
        in_failed_registry = job.opt_id in failed_registry or job.opt_id in canceled_registry
        is_status_outdated = job.status != "Failed"
        if in_failed_registry and is_status_outdated:
            job.status = "Failed"
    return jobs_list

def get_DataGridEntries(session: Session, facility_ids: list | None = None) -> dict:
    from backend.core.data_models.output_models import FacilityRow, FacilityPathwaysRow, FacilityGroupsRow, FacilityResourceRow, DataGridEntries
    from backend.core.data_models.input_models import Facility, Pathway, PatientsGroup, FacilityPathways, FacilityResources
    """Returns the data for the Datagrid components in frontend"""

    query_facilities = select(Facility)
    if facility_ids:
        query_facilities = query_facilities.where(Facility.id.in_(facility_ids))
    facilities = session.exec(query_facilities).all()
    facilities_info = getFacilitiesInfo([f.id for f in facilities])

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
    resources_entries = [FacilityResourceRow(facility_id = fr.facility_id, resource_id=fr.resource_id, capacity=fr.capacity,
                                              max_transferable_in=fr.max_transferable_in, max_transferable_out=fr.max_transferable_out) for fr in resources]
  
    query_groups = select(PatientsGroup, FacilityPathways.facility_id)\
        .join(Pathway, Pathway.group_id == PatientsGroup.id)\
            .join(FacilityPathways, FacilityPathways.pathway_id == Pathway.id)
    if facility_ids:
        query_groups = query_groups.where(FacilityPathways.facility_id.in_(facility_ids)).distinct()
    patients_groups =  session.exec(query_groups).unique().all()
    groups_entries = [FacilityGroupsRow(facility_id= facility_id, group_id=pg.id, lbl=pg.lbl, pathways=[p.id for p in pg.pathways]) for pg, facility_id in patients_groups]

    instance_entry = session.exec(select(Instance)).one_or_none()
    if instance_entry:
        entry = DataGridEntries(
            facilities= [FacilityRow(facility_id=f.id, facility_name=f.name, facility_type=f.facility_type,\
                                    info=facilities_info.get(f.id,{})) for f in facilities],
            pathways= pathways_entries,
            resources= resources_entries,
            patients_groups= groups_entries,
            instance = instance_entry
        )
    return entry.model_dump() if instance_entry else {}

def getFacilitiesInfo(list_finess) -> dict:
    import pandas as pd
    import numpy as np 
    cols = ["rslongue", "voie", "codepostal", "liblongcategetab", "siret", "liblongmft"]
    df = pd.read_csv("backend/data/open_data/finess_2018.csv", sep=";", encoding="latin1",\
                            usecols=["nofinesset"] + cols,  dtype={"coordx": str, "coordy": str},\
                            low_memory=False)
    df["nofinesset"] = df["nofinesset"].astype(str)
    df = df.set_index("nofinesset")
    

    return df.reindex(list_finess)[cols].replace({np.nan: None}).to_dict(orient="index")


def getClosestRegion(session, lat, lon):
    import math
    min_distance = math.inf
    closest_region = None

    facilities = session.exec(select(Facility)).all()
    for f in facilities:
        p1 = coords_to_point(lat,lon)
        p2 = coords_to_point(f.lat, f.lon)
        distance = p1.distance(p2).iloc[0]
        if distance < min_distance:
            min_distance = distance
            closest_region = f.region_id        

    return closest_region


def createLinkedFacilities(session, new_facility):
    from backend.core.data_models.input_models import LinkedFacilities

    linked_facilities = []
    facilities = session.exec(select(Facility)).all()
    for f in facilities:
        linked_facilities.append(LinkedFacilities(facility_id=new_facility.id, linked_facility_id=f.id))
        if f.id == new_facility.id: continue
        linked_facilities.append(LinkedFacilities(facility_id=f.id, linked_facility_id=new_facility.id))
    session.add_all(linked_facilities)


def createAffinitiesMatrix(session, new_facility):
    from backend.core.data_models.input_models import FacilityAffinity

    regions = session.exec(select(Region)).all()    
    affinities = []

    facility_point = coords_to_point(new_facility.lat, new_facility.lon)
    for region in regions: 
        affinity_score = getAffinity(region,facility_point)
        affinities.append(FacilityAffinity(facility_id=new_facility.id, region_id=region.id, affinity_score=affinity_score))

    session.add_all(affinities)
 

def coords_to_point(lat,lon):
    import geopandas as gpd
    from shapely.geometry import Point
    return (
        gpd.GeoSeries([Point(float(lon), float(lat))], crs="EPSG:4326")\
            .to_crs("EPSG:2154")
    )
    


def getAffinity(region: Region, facility_point):
    import geopandas as gpd
    from shapely.geometry import Point
    region_point = gpd.GeoSeries([Point(float(region.lon), float(region.lat))],crs="EPSG:4326").to_crs("EPSG:2154")
    distance = facility_point.iloc[0].distance(region_point.iloc[0])
    if distance == 0: score = 1/100 
    else: score = 1 / distance
    return score


def clear_all_tables(session):
    from sqlmodel import text, SQLModel
    session.exec(text("PRAGMA foreign_keys=OFF"))  # SQLite only
    try:
        for table in reversed(SQLModel.metadata.sorted_tables):
            if table.name != "job":
                session.exec(text(f"DELETE FROM {table.name}"))
    except Exception:
        print("Exception in table deletion...")
        session.rollback()
     



def run_optimization(params: dict) -> Tuple[str, str, list, dict]:
    """Returns status, objective function as str and a dict of result variables"""
    from backend.core.main import run_driver
    
    check_executable()
    print("Starting optimization driver...")
    status, objective, vars_system = run_driver(params)

    print("Optimization driver finished with status:", status)
    objective_str = f"{objective:.2f}" if objective is not None else None
    return status, objective_str, vars_system



def save_results(job_id:str, status, dict_results:dict) -> str:
    import os
    import pickle

    path = f"experiments/jobs/job_{job_id}"

    os.makedirs(path,exist_ok=True)

    with open(f"experiments/jobs/job_{job_id}/status","w") as fp:
        fp.write(status)
    with open(f"experiments/jobs/job_{job_id}/result.pkl","wb") as fp:
        pickle.dump(dict_results, fp)
    return job_id
 

def save_params_into_file(job_id:str,  params: dict) -> str:
    import os
    import json

    path = f"experiments/jobs/job_{job_id}"

    os.makedirs(path, exist_ok=True)
    with open(f"experiments/jobs/job_{job_id}/params.json","w") as fp:
        json.dump(params, fp)

    return job_id

def load_params(job_id: str) -> dict:
    import json
    with open(f"experiments/jobs/job_{job_id}/params.json","r") as fp:
        params = json.load(fp)
    return params

def load_results(job_id: str) -> dict:
    import pickle 
    with open(f"experiments/jobs/job_{job_id}/result.pkl","rb") as fp:
       results = pickle.load(fp)

    return results


def submit_optimization(job_id) -> Tuple:

    from backend.db import engine
    from backend.core.mappers.input_mappers import convert_dm_to_json

    with Session(engine) as session:
        params = convert_dm_to_json(session)
        save_params_into_file(job_id, params)
        status, _, vars_system = run_optimization(params)
        update_job_status(session, job_id, status)
        return status, vars_system


def submit_generate(job_id, instance_type, dep_code):
    from backend.db import engine

    from backend.core.mappers.datasets_mappers.maternities_serializer import serialize_maternities
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth

    with Session(engine) as session:
        try:
            if instance_type == "maternities": params = serialize_maternities(region_code = None, dep_code = dep_code, save_params=False)
            elif instance_type == "pthptg": params =serialize_ptgpth(dep_code= dep_code, p_transf = 0, p_orth= 0,
                                                                        resources_mult= 1, quality_requirement= False, save_params= False)
            #save_instance_into_db(params , session)
            #update_instance(session, instance)
            #instance = session.exec(select(Instance)).one()
            
            save_params_into_file(job_id, params)
            print(f"saving dataa for department {params["dep_code"]} into {job_id}")
            update_job_status(session, job_id, "Running")
            return params
        
        except Exception:
            update_job_status(session, job_id, "Failed")
            raise 

    
    