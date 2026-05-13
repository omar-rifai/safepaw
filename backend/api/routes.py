from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session


api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}

@api.post("/optimize")
async def optimize(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import run_optimization
    from backend.core.mappers.input_mappers import convert_dm_to_json
    import traceback
    try: 
       params_system = convert_dm_to_json(session)
       status, objective_str, dict_results = run_optimization(params_system)  
       return JSONResponse(status_code=200, content = {"status": status, "obj_val": objective_str,"results": dict_results})
       
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")




@api.put("/facilities/{id}")

async def update_facility(id: int, payload: dict = Body(...)) -> JSONResponse:
    import traceback
    from backend.api.services import unify_updated_facility
    try:
        facilities = payload["facilities"]
        updated = payload["updated"]
        for h in facilities:
            if str(h["facility_id"]) == str(id):
                unified = unify_updated_facility(payload["mode"], updated)
                print("before:", h)
                print("unified:", unified)
                h.update(unified)
                print("after:", h)
        return JSONResponse(status_code=200, content = {"facilities": facilities})
        
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.post("/read_file")
async def read_maternites(params: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    import traceback
    from backend.api.services import get_bounding_box, clear_all_tables
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json
    from backend.api.services import get_facilities_capacities, get_DataGridEntries

    try:
        clear_all_tables(session)
        session = convert_dm_from_json(params, session)
        session.commit()
        facilities_capacities = get_facilities_capacities(session)
        data_grid_entries = get_DataGridEntries(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "bbox": get_bounding_box(params)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
