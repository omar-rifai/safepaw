from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}

@api.post("/optimize")
async def optimize(payload: dict = Body(...)) -> JSONResponse:
    from backend.api.services import run_optimization
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.mappers.output_mappers import create_facilityStats
    from backend.core.data_models.input_models import SystemData
    import traceback
    try: 
        if payload["steps"]["preprocess"]:
            data = SystemData.model_validate(payload["data"])
            params = convert_dm_to_json(data)
        else:
            params = payload["data"]
        
        if payload["steps"]["optimize"]:
            status, objective_str, dict_results = run_optimization(params, params["mode"])  

            if payload["steps"]["postprocess"] and payload["steps"]["optimize"]:
                list_facility_load = [pt.as_geojson_feature() for pt in  create_facilityStats(dict_results, params)]
    
                return JSONResponse(status_code=200, content = {"status": status, "results": {"list_facility_load": list_facility_load,
                                                                                               "regions": list(params["regions_metadata"].keys())}})
            
            return JSONResponse(status_code=200, content = {"status": status, "obj_val": objective_str,"results": dict_results})
        
        return JSONResponse(status_code=200, content = {"status": None, "obj_val": None,"results": params})

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
async def read_maternites(params: dict = Body(...)) -> JSONResponse:
    import traceback
    from backend.api.services import get_bounding_box
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json
    from backend.api.services import get_facilities_capacities
    from sqlmodel import create_engine, SQLModel, Session

    try:
        request_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(request_engine)
        with Session(request_engine) as session:
            convert_dm_from_json(params, session)
            facilities_capacities = get_facilities_capacities(session)

        print("facilities_capacities:", facilities_capacities)
        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "bbox": get_bounding_box(params)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
