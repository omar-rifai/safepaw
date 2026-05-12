## Create Dataclasses
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class GroupPathways(SQLModel, table=True):
    group_id: str = Field(foreign_key="patientsgroup.id",primary_key=True)
    pathway_id: str = Field(foreign_key="pathway.id",primary_key=True)
    
    

class GroupBenefit(SQLModel, table=True):
    pathway_id: str = Field(foreign_key="pathway.id",primary_key=True)
    group_id: str = Field(foreign_key="patientsgroup.id",primary_key=True)
    benefit: float

class PathwayActivities(SQLModel, table=True):
    pathway_id: str = Field(foreign_key="pathway.id",primary_key=True)
    activity_id: str = Field(foreign_key="activity.id", primary_key=True)

class FacilityAffinity(SQLModel, table=True):
    facility_id: str  = Field(default = None, foreign_key="facility.id", primary_key=True)
    region_id : str = Field(default = None, foreign_key="region.id", primary_key=True)
    affinity_score: float


class FacilityResources(SQLModel, table=True):
    facility_id: str  = Field(default = None, foreign_key="facility.id", primary_key=True)
    resource_id: str = Field(default = None, foreign_key="resource.id", primary_key=True)
    capacity: int
    max_transferable_in: float
    max_transferable_out: float 

class FacilityPathways(SQLModel, table=True):
    facility_id: str  = Field(default = None, foreign_key="facility.id", primary_key=True)  
    pathway_id: str = Field(default = None, foreign_key="pathway.id", primary_key=True)


class LinkedFacilities(SQLModel, table=True):
    facility_id: str  = Field(default = None, foreign_key="facility.id", primary_key=True)  
    linked_facility_id: str = Field(default = None, foreign_key="facility.id", primary_key=True)  
    

class ActivityResources(SQLModel, table=True):
    activity_id: str  = Field(default = None, foreign_key="activity.id", primary_key=True)  
    resource_id: str = Field(default = None, foreign_key="resource.id", primary_key=True)  
    required_capacity: int



class CaseMixRatios(SQLModel, table=True):
    group_id: str  = Field(default = None, foreign_key="patientsgroup.id", primary_key=True)  
    region_id: str  = Field(default = None, foreign_key="region.id", primary_key=True)  
    ratio: float

class TreatmentBounds(SQLModel, table=True):
    group_id: str  = Field(default = None, foreign_key="patientsgroup.id", primary_key=True)  
    min_treatment_bound: float
    max_treatment_bound: float


class QualityBounds(SQLModel, table=True):
    group_id: str  = Field(default = None, foreign_key="patientsgroup.id", primary_key=True)  
    quality_id: str = Field(default = None, primary_key=True)
    min_quality_bound: float
    max_quality_bound: float


""" Base Objects """


class Region(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    lbl: str | None
    lat: str | None
    lon: str | None
    region_code: str | None
    dep_code: str | None
    comm_code: str | None
    can_code: str | None

    affinities: List["FacilityAffinity"] = Relationship()

    @property
    def facilities_affinity(self) -> dict:
        return {fa.facility_id: fa.affinity_score for fa in self.affinities}


class Resource(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    transfer_unit: float  

class Facility(SQLModel, table=True):
    id : str = Field(default=None, primary_key=True)
    name: str | None
    facility_type: str | None
    region_id: str = Field(default=None, foreign_key="region.id")
    lat : float| None
    lon : float | None
    nbr_visits: Optional[float] = None
    facility_resources: List["FacilityResources"] = Relationship()
    facility_pathways: List["FacilityPathways"] = Relationship()
    linked: List["LinkedFacilities"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[LinkedFacilities.facility_id]",
            "primaryjoin": "Facility.id == LinkedFacilities.facility_id"
        }
    )

    @property
    def resources_capacity(self) -> dict:
        return {fr.resource_id: fr.capacity for fr in self.facility_resources}

    @property
    def max_transferable_in(self) -> dict:
        return {fr.resource_id: fr.max_transferable_in for fr in self.facility_resources}

    @property
    def max_transferable_out(self) -> dict:
        return {fr.resource_id: fr.max_transferable_out for fr in self.facility_resources}

    @property
    def available_pathways(self) -> list:
        return [fp.pathway_id for fp in self.facility_pathways]

    @property
    def linked_facilities(self) -> list:
        return [lf.linked_facility_id for lf in self.linked]


class PatientsGroup(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)   
    lbl:str | None
    pathways: List["Pathway"] = Relationship(back_populates="groups",
                                             link_model=GroupPathways)


class Pathway(SQLModel, table=True):
    id : str = Field(default=None, primary_key=True)
    quality_level: str 
    activities: List["Activity"] = Relationship(back_populates="pathways", link_model=PathwayActivities)
    groups : List["PatientsGroup"] = Relationship(back_populates="pathways", link_model=GroupPathways)
    group_benefits : list["GroupBenefit"] = Relationship()

    @property
    def group_benefit(self) -> dict:
        return {gb.group_id: gb.benefit for gb in self.group_benefits}

class Activity(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    transferable: bool
    transfer_to: str | None = Field(default=None, foreign_key="activity.id")
    pathways: List["Pathway"] = Relationship(back_populates="activities", link_model=PathwayActivities)
    activity_resources: List["ActivityResources"] = Relationship()

    @property
    def associated_pathways(self) ->  list:
        return [pathways.id for pathways in self.pathways]

    @property
    def required_resources(self) -> dict:
        return {ar.resource_id: ar.required_capacity for ar in self.activity_resources}


class Instance(SQLModel, table=True):
    id: str = Field(default="default",primary_key=True) # the optimization ``mode'' we want to run
    perc_demand: float
    perc_capacity: float
    perc_transfers: float
    alpha: float
    
 
    