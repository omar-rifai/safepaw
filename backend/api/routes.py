from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
import pandas as pd

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}

@api.post("/optimize")
async def optimize(params: dict = Body(...)) -> JSONResponse:
    from backend.api.services import run_optimization
    import traceback

    try: 
        status, objective_str, dict_results = run_optimization(params)
        solution_json = {
            str(var): val.to_dict(orient="records")
            for var, val in dict_results.items()
        }
        return JSONResponse(
            status_code=200,
            content = {
                "status": status,
                "obj_val": objective_str,
                "results": solution_json
            }
        )

    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.post("/optimize_maternite")
async def optimize_maternite(payload = Body(...)) -> JSONResponse:
    from backend.api.services import run_optimization_maternite
    import pandas as pd 
    import traceback
    df_instance = pd.DataFrame(payload.get("dict_instance"))
    transfers = float(payload.get("transfers"))
    if "3" not in df_instance["facility_type"].unique():
        return {
            "status": "Infeasible",
            "details": "Missing facility of type 3",
            "results": None
        }
    try:
        status, avg_distance, list_patient_transfers, list_facility_load, list_facility_load_regions, regions =\
              run_optimization_maternite(df_instance, transfers)

        return {
                "status": status,
                "results": {"avg_distance": avg_distance,
                        "list_patient_transfers": [pt.as_geojson_feature() for pt in list_patient_transfers],
                        "list_facility_load": [pt.as_geojson_feature() for pt in list_facility_load],
                        "list_facility_load_regions" : [pt.as_geojson_feature() for pt in list_facility_load_regions],
                        "regions": regions}
            }
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:")
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
