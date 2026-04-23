from fastapi import APIRouter, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse
from backend.api.services import  ExecutableNotFound
import tempfile

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




@api.post("/update_maternites")
async def update_maternites(payload = Body(...)) -> JSONResponse:
    from backend.api.services import get_facility_capacity
    from backend.api.services import get_maternite_dashboard, get_region_code, get_department_code
    from backend.core.mappers.datasets_mappers.maternite_serializer import get_Facilities
    import pandas as pd
    import traceback

    try:
        if not payload.get("region"):
            return JSONResponse(
                status_code=200,
                content=payload,
            )
        else:
            region_name =  payload.get("region")
            dep_name = payload.get("department")

            df_instance = pd.DataFrame([x.model_dump(mode="python") for x in get_Facilities(get_region_code(region_name),
                                                                                            get_department_code(dep_name))])
            if "global_capacity" in payload:
                perc = payload["global_capacity"] / 100
                df_instance["resources_capacity"] = df_instance["resources_capacity"].apply(lambda x :  x | {"cap": int(x["cap"] + x["cap"] * perc)})
                
            if "demand" in payload:
                perc = payload["demand"] / 100
                df_instance["nbr_visits"] = df_instance["nbr_visits"].apply(lambda x : int(x + x * perc))
            
            list_facility_load = get_facility_capacity(df_instance)
            dashboard_stats = get_maternite_dashboard(df_instance)
        
        return JSONResponse(status_code=200, content={**payload,  "dict_instance": df_instance.to_dict(orient="records"),
                                                       "list_facility_load": list_facility_load,
                                                       "dashboard_stats": dashboard_stats,
                                                       "demand_total":  int(df_instance["nbr_visits"].sum()),
                                                       "capacity_total": int(sum([x["cap"] for x in df_instance["resources_capacity"]]))
                                                       })
        
    except Exception as e:
        print("Error in update route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")




@api.post("/read_transplants")
async def read_maternites(payload = Body(...)) -> JSONResponse:
    import traceback
    from backend.api.services import get_facility_capacity
    from backend.api.services import get_maternite_dashboard
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import read_ptgpth

    try:
    
        department = payload.get("department")
        df_instance = read_ptgpth(dep_code=str(department))
        
        list_facility_load = get_facility_capacity(df_instance)
        dashboard_stats = get_maternite_dashboard(df_instance)
       
        return JSONResponse(
            status_code=200,
            content={
                "dict_instance": df_instance.to_dict(orient="records"),
                "dashboard_stats": dashboard_stats,
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


@api.post("/read_maternites")
async def read_maternites(payload = Body(...)) -> JSONResponse:
    import traceback
    import pandas as pd
    from backend.api.services import get_department_code, get_region_code
    from backend.api.services import get_facility_capacity
    from backend.api.services import get_maternite_dashboard
    from backend.core.mappers.datasets_mappers.maternite_serializer import get_Facilities

    try:
        region_name =  payload.get("region")
        region_code = get_region_code(region_name)
        
        dep_name = payload.get("department")
        if dep_name : dep_code = get_department_code(dep_name)
        else: dep_code = None

        df_instance = pd.DataFrame([x.model_dump(mode="python") for x in get_Facilities(region_code, dep_code)])
        dashboard_stats = get_maternite_dashboard(df_instance)
        list_facility_load = get_facility_capacity(df_instance)

        return JSONResponse(
            status_code=200,
            content={
                "dict_instance": df_instance.to_dict(orient="records"),
                "dashboard_stats": dashboard_stats,
                "region": region_name,
                "department": dep_name,
                "list_facility_load": list_facility_load,
                "demand_total":  int(df_instance["nbr_visits"].sum()),
                "capacity_total": sum([int(x["cap"]/365) for x in df_instance["resources_capacity"]])
            },
        )

    except Exception:
        print("Error in api.maternites route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")



@api.post("/read_maternites_file")
async def read_maternites(params: dict = Body(...)) -> JSONResponse:
    import traceback
    import pandas as pd
    from backend.core.mappers.input_mappers_reverse import create_Facilities_from_json
    from backend.api.services import get_facility_capacity
    from backend.api.services import get_maternite_dashboard

    try:
        df_instance = pd.DataFrame([x.model_dump(mode="python") for x in create_Facilities_from_json(params)])
        print("here", df_instance)
        dashboard_stats = get_maternite_dashboard(df_instance)
        list_facility_load = get_facility_capacity(df_instance)

        return JSONResponse(
            status_code=200,
            content={
                "dict_instance": df_instance.to_dict(orient="records"),
                "dashboard_stats": dashboard_stats,
                "region": None,
                "department": None,
                "list_facility_load": list_facility_load,
                "demand_total":  int(df_instance["nbr_visits"].sum()),
                "capacity_total": sum([int(x["cap"]/365) for x in df_instance["resources_capacity"]])
            },
        )

    except Exception:
        print("Error in api.maternites route:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
