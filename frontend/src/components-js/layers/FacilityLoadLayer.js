import { ScatterplotLayer } from "@deck.gl/layers";

export function FacilityLoadLayer({ loads, setDeckGLData }) {

    const facilityLoad = (loads || []).filter(d => !d.properties?.region);

    if (facilityLoad.length === 0) {
        return null;
    }
    const maxTotalLoadFacility = Math.max(...facilityLoad.map(d => d.properties.load))
    const maxTotalCapacityFacility = Math.max(...facilityLoad.map(d => d.properties.capacities["0"]))

    return new ScatterplotLayer
        ({
            id: 'facilities-volume',
            data: facilityLoad,
            getPosition: d => d.geometry.coordinates,
            getRadius: d => {
                const delta_plus = Math.round(d.properties.transfers_in["0"])
                const delta_minus = Math.round(d.properties.transfers_out["0"])
                const capacity = Math.round(d.properties.capacities["0"])
                const capacity_w_trf = capacity + Number(delta_plus) - Number(delta_minus)
                return [4 + 6 * (capacity_w_trf / maxTotalCapacityFacility)]
            },
            getFillColor: d => {
                const delta_plus = Math.round(d.properties.transfers_in["0"])
                const delta_minus = Math.round(d.properties.transfers_out["0"])
                const capacity = Math.round(d.properties.capacities["0"])
                const capacity_w_trf = capacity + Number(delta_plus) - Number(delta_minus)
                const load = Number(d.properties.load)
                const usage = capacity_w_trf ? Math.min(load * 4.6 / capacity_w_trf, 1) : 0

                return [
                    Math.round(255 * usage),
                    0,
                    Math.round(255 * (1 - usage)),
                    Math.max(40, Math.round(usage * 150))
                ]
            },
            getLineColor: [255, 255, 255, 180],
            lineWidthMinPixels: 2,
            radiusUnits: 'pixels',
            pickable: true,
            onClick: info => {
                if (info.object) {
                    setDeckGLData(info.object);
                }
            }
        })
}

export function getFacilityToolTip(info) {

    const delta_plus = Math.round(info.object.properties.transfers_in["0"])
    const delta_minus = Math.round(info.object.properties.transfers_out["0"])
    const capacity = Math.round(info.object.properties.capacities["0"])
    const capacity_w_trf = capacity + Number(delta_plus) - Number(delta_minus)
    const load = Number(info.object.properties.load)
    const usage = capacity_w_trf ? Number(load * 4.6 / capacity_w_trf).toPrecision(2) * 100 : 0

    return {
        text: `Facility: ${info.object.properties.facility_id}\n
        Patients: ${Math.round(load)}\n
        Beds: ${capacity / 365} + ${delta_plus / 365} - ${delta_minus / 365} \n 
        Usage(%): ${usage.toPrecision(3)} `
    };
}