from pydantic import BaseModel, Field
from typing import Optional


class FacilityCapacity(BaseModel):
    facility_id: str
    facility_type: str = None
    resources_capacity: dict = Field(default_factory=dict)
    coordinates: list


class FacilityRow(BaseModel):
    facility_id: str
    facility_name: str
    facility_type: str
    

class PathwayRow(BaseModel):
    pathway_id: str
    group_id: str
    quality_level: str
    group_benefit: float
    activities: list

class ResourceRow(BaseModel):
    resource_id: str
    transfer_unit: float
    capacity: Optional[float] = None

class PatientsGroupRow(BaseModel):
    group_id: str
    lbl: Optional[str] = None
    pathways: list

class DataGridEntries(BaseModel):
    facilities: list[FacilityRow] = Field(default_factory=list)
    pathways: list[PathwayRow] = Field(default_factory=list)
    resources: list[ResourceRow] = Field(default_factory=list)
    patients_groups: list[PatientsGroupRow] = Field(default_factory=list)

class FacilityLoad(BaseModel):
    facility_id: str
    facility_type: Optional[str] = None
    coordinates: list
    patient_group: Optional[str] = None
    patient_pathway: Optional[str] = None
    region_id : Optional[str] = None
    load: Optional[float] = None
    usage: Optional[dict] = Field(default_factory=dict)
    capacities: Optional[dict] = Field(default_factory=dict)
    transfers_in: Optional[dict] = Field(default_factory=dict)
    transfers_out: Optional[dict] = Field(default_factory=dict)

    def as_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": self.coordinates},
            "properties": self.model_dump(exclude={"coordinates"}),
        }


class PatientTransfer(BaseModel):
    patients_group_id: Optional[str] = None
    pathway_id: Optional[str] = None
    origin_coordinates: list
    destination_coordinates: list
    volume: float

    def as_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    self.origin_coordinates,
                    self.destination_coordinates,
                ],
            },
            "properties": self.model_dump(
                exclude={"origin_coordinates", "destination_coordinates"}
            ),
        }


class ResourceTransfer(BaseModel):
    resource_type: str
    origin_coordinates: list
    destination_coordinates: list
    volume: float
    def as_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    self.origin_coordinates,
                    self.destination_coordinates,
                ],
            },
            "properties": self.model_dump(
                exclude={"origin_coordinates", "destination_coordinates"}
            ),
        }


class RegionalSummary(BaseModel):
    region_id: str
    coordinates: list
    patients_group: Optional[str] = None
    volume: float
    def as_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": self.coordinates},
            "properties": self.model_dump(exclude={"coordinates"}),
        }
 