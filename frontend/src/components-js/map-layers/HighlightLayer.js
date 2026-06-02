import { ScatterplotLayer } from "@deck.gl/layers";


export function HighlightLayer({ facilities, selectedFacilityID}) {

    if (facilities.length === 0) {
        return null;
    }
    const highlighted_facility = facilities.filter(d => d.facility_id == selectedFacilityID);
    return new ScatterplotLayer
        ({
            id: 'highlight',
            data: highlighted_facility,
            getPosition: d => d["coordinates"],
            getRadius: d => 50,
            getFillColor: [255, 244, 26, 80],
            getLineColor: [255, 255, 255, 180],
            lineWidthMinPixels: 2,
            radiusUnits: 'pixels',
            pickable: false,
            updateTriggers: {
                getFillColor: selectedFacilityID
            }
        })
};
