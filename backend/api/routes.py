from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session
from backend.core.data_models.input_models import Facility
from backend.api.services import get_facilities_capacities, get_DataGridEntries, get_bounding_box
import traceback

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}

@api.post("/optimize")
async def optimize(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import run_optimization
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.mappers.output_mappers import create_facilityLoad

    import traceback
    try: 
       params = convert_dm_to_json(session)
       import json
       with open("experiments/test.json", "w") as fp:
           json.dump(params, fp)
       status, objective_str, dict_results = run_optimization(params)  
       list_facility_load = [pt.as_geojson_feature() for pt in  create_facilityLoad(dict_results, params)]
       return JSONResponse(status_code=200, content = {"status": status, "results": {"list_facility_load": list_facility_load,
                                                                                               "regions": list(params["regions_metadata"].keys())}})
     
       
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.put("/update_facility/{facility_id}")
async def update_facility_type(facility_id: str, payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    

    try:
 
        facility = session.get(Facility, facility_id)
        for key, value in payload.items():
            if hasattr(facility, key):
                setattr(facility, key, value)

        session.add(facility)
        session.commit()
        session.refresh(facility)

        facilities_capacities = get_facilities_capacities(session)
        data_grid_entries = get_DataGridEntries(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "bbox": get_bounding_box(session)
            },
        )

    except HTTPException:
        raise  
    except Exception:
        session.rollback() 
        print("Error in update_facility route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



@api.put("/facilities/{id}")
async def read_facility(id: str, payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
   
    try:
        facility_id = None if id == "all" else id
        facilities_capacities = get_facilities_capacities(session, facility_id)
        data_grid_entries = get_DataGridEntries(session, facility_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "bbox": get_bounding_box(session)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        session.rollback() 
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

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "bbox": get_bounding_box(session)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
