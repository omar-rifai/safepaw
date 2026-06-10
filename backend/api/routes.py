from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session, select
from backend.core.data_models.input_models import FacilityResources, Facility, FacilityAffinity,FacilityPathways, Pathway, Resource, LinkedFacilities
from backend.api.services import get_facilities_capacities, get_DataGridEntries, get_bounding_box, get_InstanceData
import traceback, json

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}
    

@api.get("/newFacillityID")
async def newFacilityID(session: Session = Depends(get_session)) -> JSONResponse:
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
async def addFacility(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
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


@api.delete("/deleteFacility/{facility_id}")
async def delete_facility(facility_id: str, session: Session = Depends(get_session)) -> JSONResponse:
    from sqlalchemy import delete
    import traceback
    

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



@api.post("/optimize")
async def optimize(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import run_optimization, update_instance
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.mappers.output_mappers import create_facilityLoad
    import traceback
    
    try: 
       update_instance(session, payload["instance"])
       params = convert_dm_to_json(session)
       
       status, _, dict_results = run_optimization(params)  
       list_facility_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params)]
       list_facility_region_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params, by_region=True)]
       return JSONResponse(status_code=200, content = {"status": status, "facilities_loads": list_facility_load, "facilities_regions_loads": list_facility_region_load})
     
       
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=repr(e))


@api.post("/generate")
async def generate(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    import traceback
    from backend.core.mappers.datasets_mappers.maternities_serializer import serialize_maternities
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth
    from backend.api.services import  clear_all_tables
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json

    try:
        clear_all_tables(session)
        if payload["mode"] == "maternities": params = serialize_maternities(region_code = None, dep_code=payload["dep_code"], save_params=False)
        elif payload["mode"] == "pthptg": params =serialize_ptgpth(dep_code=payload["dep_code"], p_transf = 1, p_orth= 0,
                                                                    resources_mult= 1, quality_requirement= False, save_params= False)
    
        convert_dm_from_json(params, session)
        session.commit()
        facilities_capacities = get_facilities_capacities(session)
        data_grid_entries = get_DataGridEntries(session)
        instance_data = get_InstanceData(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "instance_data": instance_data,
                "bbox": get_bounding_box(session)
            },
        )

    except Exception as e:
        print("Error in api.generate route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@api.put("/update_FacilityResources")
async def update_facility_type(payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    
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
async def read_maternites(params: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    import traceback
    from backend.api.services import  clear_all_tables
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json

    try:
        clear_all_tables(session)
        convert_dm_from_json(params, session)
        session.commit()
        facilities_capacities = get_facilities_capacities(session)
        data_grid_entries = get_DataGridEntries(session)
        instance_data = get_InstanceData(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "instance_data": instance_data,
                "bbox": get_bounding_box(session)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.get("/state")
async def get_state(session: Session = Depends(get_session)):
    try:
        facilities_capacities = get_facilities_capacities(session)
        data_grid_entries = get_DataGridEntries(session)
        instance_data = get_InstanceData(session)

        return {
            "facilities_capacities": [f.model_dump() for f in facilities_capacities],
            "entries": data_grid_entries,
            "instance_data": instance_data,
            "bbox": get_bounding_box(session)
        }

    except Exception:
        print("Error in api.state route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
