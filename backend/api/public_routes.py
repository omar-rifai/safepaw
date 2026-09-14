
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional
from backend.core.utils.data_utils import package_results
from backend.core.main import run_driver
public_api = APIRouter(tags=["Public API"])


class OptimizationRequest(BaseModel):
    """Requestion payload for running the optimization model."""
    instance: dict[str, Any] = Field(dict, description= "Nested dictionary with parameters needed in the optimization model (c.f examples for details).")

class OptimizeResponse(BaseModel):
    status: str
    objective: float | None
    results: dict | None = None

class GenerateRequest(BaseModel):
    """Request payload for generating datasets from either French Maternities or Hip/knee Transplants"""
    mode: Literal["maternities", "ptgpth"] = Field(..., description="Dataset type to generate")
    region_code: Optional[str] = Field(None, description="INSEE region code to filter on. Mutually exclusive with dep_code.")
    dep_code: Optional[str] = Field(None, description="INSEE department code to filter on. Mutually exclusive with region_code.")
    perc_transfers: float =  Field(0.0, description="")
    global_multiplier_capacity: float = Field(1.0, description="Multiplier factor for the capacity")
    global_multiplier_demand: float = Field(1.0, description="Multiplier factor for the demand")
    global_perc_transfers: float = Field(0.0, description="Percentage of allowed resource transfers (across facilities)")


class GenerateResponse(BaseModel):
    instance: dict[str, Any] = Field(dict, description= "Nested dictionary with parameters needed in the optimization model (c.f examples for details).")



@public_api.post("/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizationRequest):
    try:
        status, objective, vars = run_driver(request.instance)
        if status == "Optimal":
            dict_results = package_results(vars, request.instance)
        else:
            dict_results = None
        return OptimizeResponse(status = status, objective = objective, results = dict_results)
    
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))

@public_api.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    from backend.core.mappers.datasets_mappers.maternities_serializer import serialize_maternities
    from backend.core.mappers.datasets_mappers.ptgpth_serializer import serialize_ptgpth

    try:
        mode = request.mode

        if mode == "maternities":
            params = serialize_maternities(region_code=request.region_code, dep_code=request.dep_code, save_params=False,
                                global_multiplier_demand= request.global_multiplier_demand,
                                global_multiplier_capacity= request.global_multiplier_capacity,
                                global_perc_transfers= request.global_perc_transfers)
    
        elif mode == "ptgpth":
            params = serialize_ptgpth(dep_code=request.dep_code, p_transf=request.perc_transfers, p_orth=0, quality_requirement=False, 
                            global_multiplier_demand=request.global_multiplier_demand,
                            global_multiplier_capacity=request.global_multiplier_capacity,
                            global_perc_transfers=request.global_perc_transfers)
        return GenerateResponse(instance = params)
    except Exception as e:
            raise HTTPException(status_code=500, details=str(e))
    
