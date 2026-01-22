import { ScatterplotLayer } from "@deck.gl/layers";
export function FacilityCapacityLayer({ capacities }) {

    const facilityCapacity = (capacities || []).filter(d => !d.preperties?.region);

    if (facilityCapacity.length === 0) {
        return null;
    }

    const maxTotalCapacityFacility = Math.max(...facilityCapacity.map(d => d.properties.capacities["beds"]))

    const typeColors = {
        "1": [173, 216, 230, 180],  // light blue
        "2a": [100, 200, 150, 180], // teal/greenish
        "2b": [60, 160, 90, 180],   // medium green
        "3": [0, 100, 0, 180]       // dark green
    };

    return new ScatterplotLayer
        ({
            id: 'facilities-capacity',
            data: facilityCapacity,
            getPosition: d => d.geometry.coordinates,
            getRadius: d => 4 + 6 * (d.properties.capacities["beds"] / maxTotalCapacityFacility),
            getFillColor: d => typeColors[d.properties.facility_type] || [0, 0, 255, 100],
            getLineColor: [255, 255, 255, 180],
            lineWidthMinPixels: 2,
            radiusUnits: 'pixels',
            pickable: true,
            updateTriggers: {
                getRadius: maxTotalCapacityFacility,
            }
            
        })
}

export function getFacilityCapacityToolTip(info) {
    return {
        text: `${info.object.properties.facility_id} \n(nbr lits ${parseInt(info.object.properties.capacities["beds"])})`
    };
}