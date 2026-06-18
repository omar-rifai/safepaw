from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session, select
from backend.core.data_models.input_models import FacilityResources, Facility, FacilityAffinity,FacilityPathways, Pathway, Resource
from backend.core.data_models.jobs_model import Job
from backend.api.services import get_facilities_capacities, get_DataGridEntries
import traceback

api = APIRouter()

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
    from sqlalchemy import delete

    try: 
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        stmt = delete(Job).where(Job.id == job_id)
        session.exec(stmt)
        session.commit()
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
        stmt_facility = delete(Facility).where(Facility.id == facility_id)
        session.exec(stmt_facilityResources)
        session.exec(stmt_facilityPathways)
        session.exec(stmt_facilityAffinities)
        session.exec(stmt_facility)
        session.commit()
        return JSONResponse(status_code=200, content={"message":"Facility and associated tables deleted"})
     

    except Exception as e:
        print("Error in facility delete route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



@api.post("/submit_job")
def submit_job(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import run_optimization, update_instance, create_job
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.api.services import save_job
    import traceback
    
    try: 
        update_instance(session, payload["instance"])
        params = convert_dm_to_json(session)
        

        status, _, dict_results = run_optimization(params)  
        job_id = save_job(dict_results, params) 
        create_job(session, job_id, mode=params["mode"], dep_code=params["dep_code"])
        return JSONResponse(status_code=200, content = {"job_id": job_id})

    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@api.get("/retrieve_job/{job_id}")
def retrieve_job(job_id: str) -> JSONResponse:
    from backend.core.mappers.output_mappers import create_facilityLoad
    from backend.api.services import load_params, load_results

    try:
        params = load_params(job_id) 
        dict_results = load_results(job_id)
        list_facility_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params)]
        list_facility_region_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params, by_region=True)]
    
        return JSONResponse(status_code=200, content = {"status": "OK", "facilities_loads": list_facility_load, "facilities_regions_loads": list_facility_region_load})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@api.post("/generate")
def generate(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    # Generate a new problem instance and save into frontend DB 
    import traceback
    from backend.core.mappers.datasets_mappers.maternities_serializer import serialize_maternities
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth
    from backend.api.services import  save_instance_into_db, get_input_elements

    try:
        
        if payload["mode"] == "maternities": params = serialize_maternities(region_code = None, dep_code=payload["dep_code"], save_params=False)
        elif payload["mode"] == "pthptg": params =serialize_ptgpth(dep_code=payload["dep_code"], p_transf = 0, p_orth= 0,
                                                                    resources_mult= 1, quality_requirement= False, save_params= False)
    
        save_instance_into_db(params , session)
        response = get_input_elements(session)

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
    
    try:
        facilityResource = session.exec(select(FacilityResources)\
             .where(FacilityResources.facility_id == payload["facility_id"])\
             .where(FacilityResources.resource_id == payload["resource_id"])).first()
        
        if isinstance(payload.get("capacity"), int):
            setattr(facilityResource, "capacity", payload["capacity"])

        session.add(facilityResource)
        session.commit()
        session.refresh(facilityResource)

        data_grid_entries = get_DataGridEntries(session)
        facilities_capacities = get_facilities_capacities(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
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
    import traceback
    from backend.api.services import  get_input_elements, save_instance_into_db

    try:
        save_instance_into_db(params, session)
        response = get_input_elements(session)

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
    # Load an instance state from a job ID into database for interface use
    from backend.api.services import save_instance_into_db, get_input_elements, load_params
    
    try:
        params = load_params(job_id) 
        save_instance_into_db(params, session)
        response = get_input_elements(session)

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
        response = get_input_elements(session)
        return response

    except Exception:
        print("Error in api.get_state route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
