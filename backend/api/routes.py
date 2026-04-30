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
            status, objective_str, dict_results = run_optimization(params)  
            solution = {str(var): val.to_dict(orient="records") for var, val in dict_results.items()}
        
            if payload["steps"]["postprocess"] and payload["steps"]["optimize"]:
                list_facility_load = [pt.as_geojson_feature() for pt in  create_facilityStats(solution, params)]
    
                return JSONResponse(status_code=200, content = {"status": status, "results": {"list_facility_load": list_facility_load,
                                                                                               "regions": list(params["regions_metadata"].keys())}})
            
            return JSONResponse(status_code=200, content = {"status": status, "obj_val": objective_str,"results": solution})
        
        return JSONResponse(status_code=200, content = {"status": None, "obj_val": None,"results": params})

    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



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

@api.post("/read_file")
async def read_maternites(params: dict = Body(...)) -> JSONResponse:
    import traceback
    from backend.core.mappers.input_mappers_reverse import convert_dm_from_json

    try:
        instance = convert_dm_from_json(params)
        return JSONResponse(
            status_code=200,
            content={
                "instance": instance.to_json_dict(),
                "bbox": get_bounding_box(params)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
