from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session, select
from backend.core.data_models.input_models import FacilityResources, Facility, FacilityAffinity, LinkedFacilities, FacilityPathways, Pathway, Resource
from backend.core.data_models.jobs_model import Job
from rq import Queue
from rq.job import Job as RQJob
import os
from redis import Redis
import traceback

api = APIRouter()


print("REDIS_HOST ENV =", os.getenv("REDIS_HOST", "localhost"))
redis = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)
queue = Queue("safepaw", connection=redis)

@api.get("/")
def health():
    return {"status": "ok"}
    

@api.get("/newFacillityID")
def newFacilityID(session: Session = Depends(get_session)) -> JSONResponse:
    from sqlalchemy import Integer, func, cast
    try:
        max_id = session.exec(select(func.max(cast(Facility.id, Integer)))).one()
        next_id = (max_id or 0) + 1

    except Exception as e:
        session.rollback()
        print("Error in newFacilityID route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

    return JSONResponse(
        status_code=201,
        content={"id": next_id, "message": "New facility ID generated succesfully"}
    )


@api.post("/addFacility")
def addFacility(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import createAffinitiesMatrix, createLinkedFacilities, getClosestRegion
    try: 
       
        closest_region_id = getClosestRegion(session, lat=payload["lat"], lon=payload["lon"])         

        new_facility = Facility(id=payload["facility_id"], name = payload["facility_name"], region_id=closest_region_id, lat=payload["lat"], lon=payload["lon"])
        session.add(new_facility)
        
        remaining_resources_ids = session.exec(select(Resource.id)).all()
        for r in payload["resources"]:
            remaining_resources_ids.remove(r["resource_id"])
            new_facility_resources = FacilityResources(facility_id = payload["facility_id"], resource_id = r["resource_id"],
                                                        capacity = r["capacity"], max_transferable_in=r["max_transferable_in"], max_transferable_out=r["max_transferable_out"])
            session.add(new_facility_resources)
        for rid in remaining_resources_ids:
            new_facility_resources = FacilityResources(facility_id = payload["facility_id"], resource_id = rid,
                                                        capacity = 0, max_transferable_in=0, max_transferable_out=0)
            session.add(new_facility_resources)

     
        pathways = session.exec(select(Pathway)).all()
        
        for pathway in pathways:
            new_facility_pathway = FacilityPathways(facility_id=payload["facility_id"],pathway_id = pathway.id, group_id = pathway.group_id)
            session.add(new_facility_pathway)
        session.commit()
        createLinkedFacilities(session, new_facility)
        createAffinitiesMatrix(session, new_facility)

        session.commit() 
        session.refresh(new_facility)
    
    except Exception as e:
        session.rollback()
        print("Error in addFacility route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

    return JSONResponse(
        status_code=201,
        content={"message": "Facility created successfully"}
    )



@api.delete("/deleteJob/{job_id}")
def delete_job(job_id: str, session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import cleanup_job_entry

    try: 
        redis_job = RQJob.fetch(job_id, connection=redis)
        redis_job.cancel()
        print("canceled job status:", job.get_status())
    except Exception as e:
        pass
    try:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        cleanup_job_entry(session, job_id)
        return JSONResponse(status_code=200, content={"message":"Job sucessfuly deleted"})
        

    except Exception as e:
        print("Error in facility delete route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")




@api.delete("/deleteFacility/{facility_id}")
def delete_facility(facility_id: str, session: Session = Depends(get_session)) -> JSONResponse:
    from sqlalchemy import delete

    try: 
        facility = session.get(Facility, facility_id)
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")

        stmt_facilityResources = delete(FacilityResources).where(FacilityResources.facility_id == facility_id)
        stmt_facilityPathways = delete(FacilityPathways).where(FacilityPathways.facility_id == facility_id)
        stmt_facilityAffinities = delete(FacilityAffinity).where(FacilityAffinity.facility_id == facility_id)
        stmt_linkedFacilities = delete(LinkedFacilities).where(LinkedFacilities.facility_id == facility_id)
        stmt_facility = delete(Facility).where(Facility.id == facility_id)
        session.exec(stmt_facilityResources)
        session.exec(stmt_facilityPathways)
        session.exec(stmt_facilityAffinities)
        session.exec(stmt_linkedFacilities)
        session.exec(stmt_facility)
        session.commit()
        return JSONResponse(status_code=200, content={"message":"Facility and associated tables deleted"})
     

    except Exception as e:
        print("Error in facility delete route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



@api.post("/submit_job")
def submit_job(payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import submit_optimization, create_job_db_entry, update_job_optid, update_instance
    import uuid
    try: 
        job_id = str(uuid.uuid4())
        update_instance(session, payload["instance"])
        create_job_db_entry(session, job_id, instance=payload["instance"], mode=payload["mode"], dep_code= payload["dep_code"])
        job = queue.enqueue(submit_optimization, job_id, job_timeout=-1,  result_ttl=60*60*24)
        update_job_optid(session, job_id, job.id)
        return JSONResponse(status_code=200, content = {"job_id": job.id})

    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@api.get("/retrieve_job/{job_id}")
def retrieve_job(job_id: str, session:Session = Depends(get_session)) -> JSONResponse:
    from backend.core.mappers.output_mappers import create_facilityLoad
    from backend.core.mappers.output_mappers import get_average_distance
    from backend.api.services import load_params, load_results, save_results, save_instance_into_db, get_input_elements, updateParams
    from backend.core.utils.data_utils import package_results
    from rq.job import Job as RQJob, JobStatus

    try:
        db_entry = session.exec(select(Job).where(Job.id == job_id)).one()
        opt_id = db_entry.opt_id
        params = load_params(job_id)
        save_instance_into_db(params, session)
        input_data = get_input_elements(session, queue)
        if opt_id is None:
            return JSONResponse(status_code=202, content={"status": "pending", "input_data": input_data})

        job = RQJob.fetch(opt_id, connection=redis)
        job_status = job.get_status()

        if job_status == JobStatus.QUEUED:
    
            return JSONResponse(status_code=202, content={"status": "pending", "input_data": input_data})

        if job_status == JobStatus.STARTED:

            return JSONResponse(status_code=200, content={"status": db_entry.status, "input_data": input_data})
                
        if job_status == JobStatus.FINISHED :
            results = job.result
            optimization_status = results[0]

            dict_results = package_results(results[1], params)
            save_results(job_id, optimization_status, dict_results )
            if optimization_status == "Optimal":
                dict_results = load_results(job_id)
                params = updateParams(params)
                list_facility_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params)]
                list_facility_region_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params, by_region=True)]
                average_distance = get_average_distance(dict_results, params)
                output_data = {"facilities_loads": list_facility_load, "facilities_regions_loads": list_facility_region_load, "average_distance": average_distance}
            else: 
                output_data = {}
            
            return JSONResponse(status_code=200, content = {"status": db_entry.status, "input_data": input_data, "output_data": output_data})
        else:
            return JSONResponse(status_code=200, content = {"status": job_status, "input_data": input_data, "output_data": {}})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@api.post("/generate")
def generate(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    # Generate a new problem instance and save into frontend DB 

    from backend.core.mappers.datasets_mappers.maternities_serializer import serialize_maternities
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth
    from backend.api.services import  save_instance_into_db, get_input_elements

    try:
        print(f"dep_code is {payload["dep_code"]}")
        if payload["mode"] == "maternities": params = serialize_maternities(region_code = None, dep_code=payload["dep_code"], save_params=False)
        elif payload["mode"] == "pthptg": params =serialize_ptgpth(dep_code=payload["dep_code"], p_transf = 1, p_orth= 0,
                                                                    resources_mult= 1, quality_requirement= False, save_params= False)
    
        save_instance_into_db(params , session)

        response = get_input_elements(session, queue)

        return JSONResponse(
            status_code=200,
            content=response)

    except Exception as e:
        print("Error in api.generate route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@api.put("/update_FacilityResources")
def update_facility_type(payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import get_input_elements
    try:
        facilityResource = session.exec(select(FacilityResources)\
             .where(FacilityResources.facility_id == payload["facility_id"])\
             .where(FacilityResources.resource_id == payload["resource_id"])).first()
        
        if isinstance(payload.get("capacity"), int):
            setattr(facilityResource, "capacity", payload["capacity"])

        session.add(facilityResource)
        session.commit()
        session.refresh(facilityResource)

        input_data = get_input_elements(session, queue)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":input_data["facilities_capacities"],
                "entries": input_data["entries"],
            },
        )

    except HTTPException:
        raise  
    except Exception:
        session.rollback() 
        print("Error in update_facility route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.post("/read_file")
def read_file(params: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:

    from backend.api.services import  get_input_elements, save_instance_into_db

    try:
        save_instance_into_db(params, session)
        response = get_input_elements(session, queue)

        return JSONResponse(
            status_code=200,
            content=response
        )

    except Exception:
        print("Error in api.read_file route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.get("/load_state/{job_id}")
def load_state(job_id: str, session: Session = Depends(get_session)):
    # Load a model instance state from a job ID into database for interface use
    from backend.api.services import save_instance_into_db, get_input_elements, load_params
    
    try:
        params = load_params(job_id) 
        save_instance_into_db(params, session)
        response = get_input_elements(session, queue)

        return response

    except Exception:
        print("Error in api.load_state route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.get("/get_state")
def get_state(session: Session = Depends(get_session)):
    from backend.api.services import get_input_elements

    try:
        response = get_input_elements(session, queue)
        return response

    except Exception:
        print("Error in api.get_state route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



@api.get("/get_jobs")
def get_jobs(session: Session = Depends(get_session)):
    from backend.api.services import getJobs, cleanup_job_entry

    try:
        jobs_list = getJobs(session, queue)
        for job in jobs_list:
            try:
                RQJob.fetch(job.opt_id, connection=redis)
            except Exception:
                cleanup_job_entry(session, job.id)
                
        jobs_list = getJobs(session, queue)
        return [j.model_dump(mode="json") for j in jobs_list]

    except Exception:
        print("Error in api.get_jobs route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
