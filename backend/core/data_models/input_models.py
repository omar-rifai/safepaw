## Create Dataclasses
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List, Dict

from pathlib import Path


class Region(BaseModel):
    region_id: str
    region_lbl: Optional[str] = None
    coordinates: list
    facilities_affinity: Dict[str, float] # {facility id: affinity_score}


class Resource(BaseModel):
    resource_id: str
    resource_type: Optional[str] = None
    associated_facility: Optional[Facility] = None

class Facility(BaseModel):
    facility_id : str
    facility_name: Optional[str] = None
    region: Optional[str] = None 
    coordinates: list
    resources_capacity: Dict[str, int]
    available_pathways: List[str]
    linked_facilities: List[str]
    max_transferable_in : Dict[str, float] 
    max_transferable_out : Dict[str, float]

class PatientsGroup(BaseModel):
    group_id: str
    group_lbl: Optional[str] = None
    possible_pathways: List[str] # pathway IDs


class Pathway(BaseModel):
    pathway_id : str
    associated_group_id : str
    quality_level: str 
    list_activities : List[int]
    group_benefit : float
    list_next : List[int] # the next non-home activity if self is also non-home


class Instance(BaseModel):
    d_total: int
    d_gr : List[List[float]]  # [group_id][region ID] : min treatment threshold
    under_q_g: List[float]
    over_q_g: List[float]
    under_q_gu: List[List[float]] #[group_id][treatment lvl] : min treatment proportion
    over_q_gu: List[List[float]]
    p_transf: float # max allowable percentage of patients to be tranfered
    delta_l: List[int]  # resource id : transfer unit
    alpha: float

class Activity(BaseModel):
    activity_id: str
    associated_pathway: str
    associated_group: str
    transferable: bool
    transfer_to: str
    required_resources: Dict[str, float]


class SystemData(BaseModel):
    regions : List[Region]
    resources: List[Resource]
    facilities: List[Facility]
    patients: List[PatientsGroup]
    pathways : List[Pathway]    
    activities : List[Activity] 
    instance : Instance

     
    def to_json_str(self) -> str:
        """
        Serialize to json string
        """
        return self.model_dump_json()


    def to_json_dict(self) -> str:
        """
        Serialize to json dict
        """
        return self.model_dump()

 
    def save_json(self, path: str | Path, indent: int = 2):
        """
        Save to json file
        """
        Path(path).write_text(self.model_dump_json(indent=indent))

    @classmethod
    def from_json(cls, json_str: str) -> SystemData:
        """
        load from json string
        """
        return cls.model_validate_json(json_str)


    @classmethod
    def load_json(cls, path: str | Path) -> SystemData:
        """
        load from json file
        """
        data = Path(path).read_text()
        return cls.model_validate_json(data)
