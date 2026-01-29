from fastapi import APIRouter, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
import tempfile

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}

@api.post("/optimize")
async def optimize(file_params: UploadFile) -> JSONResponse:
    from backend.api.services import run_optimization, get_regions_metadata
    import traceback

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file_params.read())
            params_filepath = tmp_file.name
        
        original_filename = file_params.filename
        metadata_filepath = "backend/data/metadata_" + original_filename.split('_')[1]

        regions = get_regions_metadata(metadata_filepath)
        
        status, objective_str, list_patient_transfers, list_facility_load, list_facility_load_regions = run_optimization(
            params_filepath, metadata_filepath)

        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "obj_val": objective_str,
                "list_patient_transfers": [pt.as_geojson_feature() for pt in list_patient_transfers],
                "list_facility_load": [pt.as_geojson_feature() for pt in list_facility_load],
                "list_facility_load_regions" : [pt.as_geojson_feature() for pt in list_facility_load_regions],
                "regions": regions
            },
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
    if "3" not in df_instance["type"].unique():
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




@api.post("/update_maternites")
async def update_maternites(payload = Body(...)) -> JSONResponse:
    from backend.api.services import get_facility_capacity_maternite
    from backend.api.services import get_maternite_dashboard
    from backend.core.mappers.datasets_mappers.maternite_serializer import read_maternity
    import traceback

    try:
        if not payload.get("region"):
            return JSONResponse(
                status_code=200,
                content=payload,
            )
        else:
            df_maternites = read_maternity()
            df_instance = df_maternites

            region =  payload.get("region")
            department = payload.get("department")
            
            if region:
                df_instance = df_instance[df_instance["region_name"] == region ]

            if department:
                df_instance = df_instance[df_instance["dep_name"] == department ]

            if "global_capacity" in payload:
                perc = payload["global_capacity"] / 100
                df_instance["beds"] = df_instance["beds"].apply(lambda x : int(x + x * perc))
                
            if "demand" in payload:
                perc = payload["demand"] / 100
                df_instance["deliveries_per_facility"] = df_instance["deliveries_per_facility"].apply(lambda x : int(x + x * perc))
            
            list_facility_load = get_facility_capacity_maternite(df_instance)
            dashboard_stats = get_maternite_dashboard(df_instance)
        
        return JSONResponse(status_code=200, content={**payload,  "dict_instance": df_instance.to_dict(orient="records"),
                                                       "list_facility_load": list_facility_load,
                                                       "dashboard_stats": dashboard_stats,
                                                       "demand_total":  int(df_instance["deliveries_per_facility"].sum()),
                                                       "capacity_total": int(df_instance["beds"].sum())
                                                       })
        
    except Exception as e:
        print("Error in update route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")





@api.post("/read_maternites")
async def read_maternites(payload = Body(...)) -> JSONResponse:
    import traceback
    from backend.api.services import get_facility_capacity_maternite
    from backend.api.services import get_maternite_dashboard
    from backend.core.mappers.datasets_mappers.maternite_serializer import read_maternity

    try:

        df_maternites = read_maternity()
        df_instance = df_maternites
        region =  payload.get("region")
        department = payload.get("department")
        
        if region:
            df_instance = df_instance[df_instance["region_name"] == region ]

        if department:
            df_instance = df_instance[df_instance["dep_name"] == department ]


        list_facility_load = get_facility_capacity_maternite(df_instance)
        dashboard_stats = get_maternite_dashboard(df_instance)
       
        return JSONResponse(
            status_code=200,
            content={
                "dict_instance": df_instance.to_dict(orient="records"),
                "dashboard_stats": dashboard_stats,
                "region": region,
                "department": department,
                "list_facility_load": list_facility_load,
                "demand_total":  int(df_instance["deliveries_per_facility"].sum()),
                "capacity_total": int(df_instance["beds"].sum())
            },
        )

    except Exception:
        print("Error in api.maternites route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
