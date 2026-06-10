import { ScatterplotLayer } from "@deck.gl/layers";


var max_capacities;
function getMaxCapacities(loads) {

  return loads.reduce((acc, facility) => {
    const capacities = facility?.resources_capacity;
    for (const [resource, value] of Object.entries(capacities)) {
      if (!(resource in acc) || value > acc[resource]) {
        acc[resource] = value;
      }
    }
    return acc;
  }, {});
}


function jitter([lat, lng], amount = 0.00045) {
  return [
    lng + (Math.random() - 0.5) * amount,
    lat + (Math.random() - 0.5) * amount
  ];
}


function getNormalizedCapacityAvg(facilityLoad, max_capacities) {

  const normalized = Object.entries(facilityLoad.resources_capacity).map(
    ([r, v]) => {
      const delta_plus = Math.round(facilityLoad.transfers_in[r])
      const delta_minus = Math.round(facilityLoad.transfers_out[r])
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

  const use_ratios = Object.values(facilityLoad.usage)

  const sum = use_ratios.reduce((a, b) => a + b, 0);
  const avg = sum / use_ratios.length
  return avg
}


function getFillColor(obj) {
  const usage = getAvgUsage(obj) ? getAvgUsage(obj) : 0
  return [
    Math.round(255 * usage),
    0,
    Math.round(255 * (1 - usage)),
    Math.max(40, Math.round(usage * 150))
  ]
}

export function FacilityLoadLayer({ loads, selectedFacilityID, setSelectedFacilityID }) {

  if (!loads || loads.length === 0) {
    return null;
  }

  max_capacities = getMaxCapacities(loads)
  return new ScatterplotLayer
    ({
      id: 'facilities-volume',
      data: loads,
      getPosition: d => jitter(d.coordinates),
      getRadius: d => {
        const capacity = getNormalizedCapacityAvg(d, max_capacities)
        return 4 + 6 * capacity
      },
      getFillColor: d => getFillColor(d),
      getLineColor: [255, 255, 255, 180],
      lineWidthMinPixels: 2,
      radiusUnits: 'pixels',
      pickable: true,
      onClick: info => {
        if (info.object) {
          setSelectedFacilityID(info.object?.facility_id)
        }
      },
      updateTriggers: {
        getFillColor: [selectedFacilityID]
      },
    })
}

export function getFacilityToolTip(info) {
  if (!info?.object) return null;
  const facilityId = info.object["facility_id"];

  return {
    html: `
    <h3>Facility:</h3>
    <div>${facilityId}</div>
  `,
    style: {
      backgroundColor: 'rgba(254, 254, 254, 1)',
      fontSize: '0.8em'
    }
  }
};