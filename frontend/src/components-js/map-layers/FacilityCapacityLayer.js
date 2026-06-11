import { ScatterplotLayer } from "@deck.gl/layers";
import chroma from "chroma-js"



function getMaxCapacities(facilities) {
  return facilities.reduce((acc, facility) => {
    const capacities = facility?.resources_capacity;
    for (const [resource, value] of Object.entries(capacities)) {
      if (!(resource in acc) || value > acc[resource]) {
        acc[resource] = value;
      }
    }
    return acc;
  }, {});
}


function getNormalizedCapacityAvg(facility, max_capacities) {
  const normalized = Object.entries(facility.resources_capacity).map(
    ([r, v]) => {
      const curr_max = max_capacities[r];
      if (!curr_max) return 0;
      return v / max_capacities[r]
    }
  );

  const sum = normalized.reduce((a, b) => a + b, 0);
  const avg = sum / normalized.length
  return { ...facility, normalized_avg: avg }
}

const color_scale = chroma.scale(chroma.brewer.Set1)
function getColor(type) {
  if (!type) return [0, 0, 255, 100]
  const hash = [...type].reduce((a, c) => a + c.charCodeAt(0), 0);
  const [r, g, b, a] = color_scale(hash % 10 / 10).rgba();
  return [Math.round(r), Math.round(g), Math.round(b), Math.round(a * 200)];
}

function reverse([lat, lng], jitter = 0) {
  return [
    lng + (Math.random() - 0.5) * jitter,
    lat + (Math.random() - 0.5) * jitter
  ];
}

export function FacilityCapacityLayer({ facilities, selectedFacilityID, setSelectedFacilityID }) {

  if (facilities.length === 0) {
    return null;
  }
  const max_capacities = getMaxCapacities(facilities)
  const facilities_w_avg = facilities.map(f => getNormalizedCapacityAvg(f, max_capacities))

  return new ScatterplotLayer
    ({
      id: 'facilities-capacity',
      data: facilities_w_avg,
      getPosition: d => reverse(d["coordinates"]),
      getRadius: d => 4 + 6 * d.normalized_avg,
      getFillColor: d =>  getColor(d["facility_type"]),
      getLineColor: [255, 255, 255, 180],
      lineWidthMinPixels: 2,
      onClick: info => {
        setSelectedFacilityID(info.object?.facility_id);

      },
      radiusUnits: 'pixels',
      pickable: true,
      updateTriggers: {
        getRadius: facilities_w_avg,
        getFillColor: selectedFacilityID
      }
    })
}

export function getFacilityCapacityToolTip(info) {
  return info && {

    html: `
        <h3>Facility:</h3> 
        <div>${info.object.facility_id}</div>
        `,
    style: {
      backgroundColor: 'rgba(254, 254, 254, 1)',
      fontSize: '0.8em'
    }
  };
}