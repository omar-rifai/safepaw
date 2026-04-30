import { ScatterplotLayer } from "@deck.gl/layers";



function getMaxCapacities(facilityLoad) {

    return facilityLoad.reduce((acc, facility) => {
        const capacities = facility.properties.capacities;
        for (const [resource, value] of Object.entries(capacities)) {
            if (!(resource in acc) || value > acc[resource]) {
                acc[resource] = value;
            }
        }
        return acc;
    }, {});
}


function getNormalizedCapacityAvg(facilityLoad, max_capacities) {

    const normalized = Object.entries(facilityLoad.properties.capacities).map(
        ([r, v]) => {
            const curr_max = max_capacities[r];
            if (!curr_max) return 0;
            return v / curr_max
        }
    );
    const sum = normalized.reduce((a, b) => a + b, 0);
    const avg = sum / normalized.length
    return avg 
}


export function FacilityLoadLayer({ loads, setDeckGLData }) {

    if (!loads || loads.length === 0) {
        return null;
    }
    const facilityLoad = loads;


    const max_capacities = getMaxCapacities(facilityLoad)
    //const maxTotalCapacityFacility = Math.max(...facilityLoad.map(d => getNormalizedCapacityAvg(d, max_capacities).normalized_avg));

    return new ScatterplotLayer
        ({
            id: 'facilities-volume',
            data: facilityLoad,
            getPosition: d => d.geometry.coordinates,
            getRadius: d => {
                const capacity = getNormalizedCapacityAvg(d,max_capacities)
                return [4 + 6 * capacity]
            },
            getFillColor: d => {
                const load = Number(d.properties.load)
                const usage = getNormalizedCapacityAvg(d,max_capacities) ? Math.min(load * 4.6 / getNormalizedCapacityAvg(d,max_capacities), 1) : 0

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
                console.log("info on click", info.object)
                if (info.object) {
                    setDeckGLData(info.object);
                }
            }
        })
}

export function getFacilityToolTip(info) {

    const delta_plus = Math.round(info.object.properties.transfers_in["cap"])
    const delta_minus = Math.round(info.object.properties.transfers_out["cap"])
    const capacity = Math.round(info.object.properties.capacities["cap"])
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