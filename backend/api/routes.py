from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from backend.api.services import  ExecutableNotFound
from backend.db import get_session
from sqlmodel import Session, select
from backend.core.data_models.input_models import FacilityResources
from backend.api.services import get_facilities_capacities, get_DataGridEntries, get_bounding_box, get_DashboardStats
import traceback, sys, janus, threading, json, os, asyncio

api = APIRouter()

@api.get("/")
def health():
    return {"status": "ok"}


@api.get("/stream")

async def stream(instance: str, session: Session = Depends(get_session)) ->StreamingResponse:
    from backend.api.services import run_optimization
    from backend.api.services import run_optimization, update_instance
    from backend.core.mappers.output_mappers import create_facilityLoad
    from backend.core.mappers.input_mappers import convert_dm_to_json
    queue = janus.Queue()
    instance = json.loads(instance)
    
    class StdOutWriter:
        def __init__(self, sync_q):
            self.sync_q = sync_q
        def write(self, text):
            for line in text.splitlines():
                if line.strip():
                    self.sync_q.put(line)
        def flush(self): pass

    def run():
        sys.stdout = sys.stderr = StdOutWriter(queue.sync_q)
        try:
            update_instance(session, instance)
            params = convert_dm_to_json(session)
            status, _, dict_results = run_optimization(params)
            results = [f.model_dump() for f in create_facilityLoad(dict_results, params)] 
            queue.sync_q.put({"type": "result", "status": status, "facilities_loads": results})
        except Exception as e:
            print(f"ERROR: {e}", flush=True)
            traceback.print_exc()
        finally:
            sys.stdout = sys.__stdout__
            queue.sync_q.put(None)
    
    os.environ["PYTHONUNBUFFERED"] = "1"
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run)

    async def read_from_queue():
        while True:
            item = await queue.async_q.get()
            if item is None: break
            if isinstance(item, dict):
                yield f"data: {json.dumps(item)}\n\n"
            else:
                yield f'data: {json.dumps({"type":"log","message":item})}\n\n'

    return StreamingResponse(read_from_queue(), media_type="text/event-stream")


@api.post("/optimize")
async def optimize(payload: dict = Body(...), session: Session = Depends(get_session)) -> JSONResponse:
    from backend.api.services import run_optimization, update_instance
    from backend.core.mappers.input_mappers import convert_dm_to_json
    from backend.core.mappers.output_mappers import create_facilityLoad
    import traceback
    
    try: 
       update_instance(session, payload["instance"])
       params = convert_dm_to_json(session)
       
       with open("experiments/test.json", "w") as fp:
           json.dump(params, fp)
       status, _, dict_results = run_optimization(params)  
       list_facility_load = [f.model_dump() for f in  create_facilityLoad(dict_results, params)]
       return JSONResponse(status_code=200, content = {"status": status, "facilities_loads": list_facility_load})
     
       
    except ExecutableNotFound as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        print("Error in optimize route:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@api.put("/update_FacilityResources")
async def update_facility_type(payload: dict = Body(...), session:Session = Depends(get_session)) -> JSONResponse:
    
    try:
        
        facilityResource = session.exec(select(FacilityResources)\
             .where(FacilityResources.facility_id == payload["facility_id"])\
             .where(FacilityResources.resource_id == payload["resource_id"])).first()
        
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
        dashboard_stats = get_DashboardStats(session)

        return JSONResponse(
            status_code=200,
            content={
                "facilities_capacities":[f.model_dump() for f in facilities_capacities],
                "entries": data_grid_entries,
                "dashboard_stats": dashboard_stats,
                "bbox": get_bounding_box(session)
            },
        )

    except Exception:
        print("Error in api.read_file route:")
        session.rollback() 
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
