import { ScatterplotLayer } from "@deck.gl/layers";


var max_capacities;
function getMaxCapacities(loads) {

    return loads.reduce((acc, facility) => {
        const capacities = facility.properties.capacities;
        for (const [resource, value] of Object.entries(capacities)) {
            if (!(resource in acc) || value > acc[resource]) {
                acc[resource] = value;
            }
        }
        return acc;
    }, {});
}


function jitter([lng, lat], amount = 0.00045) {
  return [
    lng + (Math.random() - 0.5) * amount,
    lat + (Math.random() - 0.5) * amount
  ];
}


function getNormalizedCapacityAvg(facilityLoad, max_capacities) {

    const normalized = Object.entries(facilityLoad.properties.capacities).map(
        ([r, v]) => {
            const delta_plus = Math.round(facilityLoad.properties.transfers_in[r])
            const delta_minus = Math.round(facilityLoad.properties.transfers_out[r])
            const curr_max = max_capacities[r];
            if (!curr_max) return 0;
            return (v + delta_plus - delta_minus) / curr_max
        }
    );
    const sum = normalized.reduce((a, b) => a + b, 0);
    const avg = sum / normalized.length
    return avg 
}


function getAvgUsage(facilityLoad) {

    const use_ratios = Object.values(facilityLoad.properties.usage)

    const sum = use_ratios.reduce((a, b) => a + b, 0);
    const avg = sum / use_ratios.length
    console.log("average use:",use_ratios)
    return avg 
}

export function FacilityLoadLayer({ loads, setDeckGLData }) {

    if (!loads || loads.length === 0) {
        return null;
    }

    max_capacities = getMaxCapacities(loads)

    return new ScatterplotLayer
        ({
            id: 'facilities-volume',
            data: loads,
            getPosition: d => jitter(d.geometry.coordinates),
            getRadius: d => {
                const capacity = getNormalizedCapacityAvg(d,max_capacities)
                return [4 + 6 * capacity]
            },
            getFillColor: d => {
                const usage = getAvgUsage(d) ? getAvgUsage(d) : 0
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

    return info && {

    html: `
        <h3>Facility:</h3> 
        <div>${info.object.properties["facility_id"]}</div>
        <h3>Resources Use:</h3>
        <div style="word-break: break-all; max-width: 20em">${Object.entries(info.object.properties["usage"]).map(([k, v]) => `"${k}": ${v}\n`)}</div>
        `,
    style: {
      backgroundColor: 'rgba(254, 254, 254, 1)',
      fontSize: '0.8em'
    }
  };
}