import { ArcLayer } from "@deck.gl/layers";

export function RegionFacilityLoadLayer({ loads, selectedFacilityID }) {
    const maxLoad = loads?.reduce((max, d) => Math.max(max, d["load"]), 0);
    const facilityLoads = (loads || [])
        .filter(d => (d["facility_id"]==selectedFacilityID))
        .filter(d => (d["load"]>0))
    if (facilityLoads.length === 0) {
        return null;
    }

    return new ArcLayer
        ({
            id: 'region-to-facility',
            data: facilityLoads,
            getSourcePosition: d =>[d.region_coordinates[1], d.region_coordinates[0]],
            getTargetPosition: d => [d.coordinates[1], d.coordinates[0]],
            getSourceColor: d => {
                const t = d["load"] / maxLoad;
                return [0, Math.round(t * 255), 80, 20 + t * 255];
            },
            getTargetColor: d => {
                const t = d["load"] / maxLoad;
                return [0,Math.round(t * 255), 80 , 20 + t * 255];
            },
            getWidth: d => {
                const t = d["load"] / maxLoad;
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
    const region_lbl = Number(info.object.region_id) ?? ""
    return {
        text: `${region_lbl} Flow: ${Math.round(info.object.load)}`
    };
}