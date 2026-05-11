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
                const capacity = getNormalizedCapacityAvg(d, max_capacities)
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
  if (!info) return null;

  const usage = info.object.properties["usage"];
  const facilityId = info.object.properties["facility_id"];

  const entries = Object.entries(usage).filter(
    ([, v]) => typeof v === "number" && isFinite(v)
  );
  if (!entries.length) return null;

  const colors = [
    "#534AB7", "#1D9E75", "#D85A30", "#D4537E",
    "#378ADD", "#639922", "#BA7517", "#E24B4A"
  ];

  const miniPie = (pct, color) => {
    const filled = Math.min(Math.max(pct, 0), 1) * 360;
    return `<div style="width:40px;height:40px;border-radius:50%;background:conic-gradient(${color} 0deg ${filled.toFixed(2)}deg,#e0e0e0 ${filled.toFixed(2)}deg 360deg);flex-shrink:0;"></div>`;
  };

  const rows = entries.map(([key, val], i) => {
    const color = colors[i % colors.length];
    const pct = Math.min(Math.max(val, 0), 1);
    return `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
        ${miniPie(pct, color)}
        <div>
          <div style="font-size:11px;font-weight:bold;word-break:break-all;">${key}</div>
          <div style="font-size:11px;">${(pct * 100).toFixed(1)}%</div>
        </div>
      </div>`;
  }).join("");

  return {
    html: `
      <div style="font-family:sans-serif;font-size:12px;">
        <div style="font-weight:bold;margin-bottom:4px;">Facility: ${facilityId}</div>
        <div style="font-weight:bold;margin-bottom:8px;">Resource use:</div>
        ${rows}
      </div>`,
    style: {
      backgroundColor: "rgba(254,254,254,0.95)",
      color: "#000",
      padding: "10px",
      borderRadius: "6px",
      maxWidth: "220px"
    }
  };
}