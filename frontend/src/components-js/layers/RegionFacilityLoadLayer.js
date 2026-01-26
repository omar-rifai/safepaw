import { ArcLayer } from "@deck.gl/layers";

export function RegionFacilityLoadLayer({ loads, regions, selectedItem }) {

    if (!selectedItem.properties) { return null }

    const tolerance = 0.0001;
    const maxLoad = loads.reduce((max, d) => Math.max(max, d.properties.load), 0);

    const facilityLoads = (loads || [])
        .filter(d => d.properties.region_id != null &&
            Math.round(d.properties.load) > 0 &&
            d.properties.facility_id == selectedItem.properties.facility_id &&
            Math.abs(d.geometry.coordinates[0] - selectedItem.geometry.coordinates[0]) < tolerance &&
            Math.abs(d.geometry.coordinates[1] - selectedItem.geometry.coordinates[1]) < tolerance 
        )
    if (facilityLoads.length === 0) {
        return null;
    }

    console.log("In regionFacility loads", facilityLoads)
    return new ArcLayer
        ({
            id: 'region-to-facility',
            data: facilityLoads,
            getSourcePosition: d => regions[d.properties.region_id].coordinates,
            getTargetPosition: d => d.geometry.coordinates,
            getSourceColor: d => {
                const t = d.properties.load / maxLoad;
                return [0, 0, Math.round(t * 255), 20 + t * 255];
            },
            getTargetColor: d => {
                const t = d.properties.load / maxLoad;
                return [0, 0, Math.round(t * 255), 20 + t * 255];
            },
            getWidth: d => {
                const t = d.properties.load / maxLoad;
                return Math.min(t * 100, 5)
            },
            getHeight: 0.4,
            greatCircle: true,
            pickable: true,
            updateTriggers: {
                getTargetColor: maxLoad
            }
        })
}





export function getRegionFacilityToolTip(info, regions) {
    const region_lbl = regions ? regions[Number(info.object.properties.region_id)].name : ""
    return {
        text: `${region_lbl} Flow: ${Math.round(info.object.properties.load)}`
    };
}