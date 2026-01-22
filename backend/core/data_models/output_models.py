from pydantic import BaseModel, Field
from typing import Optional


class FacilityStats(BaseModel):
    facility_id: str
    facility_type: Optional[str] = None
    coordinates: list
    patient_group: Optional[str] = None
    patient_pathway: Optional[str] = None
    region_id : Optional[str] = None
    load: Optional[float] = None
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
 