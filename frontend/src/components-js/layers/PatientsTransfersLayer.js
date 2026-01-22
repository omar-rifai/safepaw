import { PathLayer } from "@deck.gl/layers";
import { PathStyleExtension } from '@deck.gl/extensions';


export default function PatientsTransfersLayer({ transfers }) {

    const visibleTransfers = (transfers || []).filter(d => d.properties.volume > 0);
    
    if (visibleTransfers.length === 0) {
        return null;
    }
    
    const maxTotalTransfer = Math.max(...visibleTransfers.map(d => d.properties.volume))
    
    return new PathLayer({
        id: 'patient-transfers',
        data: visibleTransfers,
        getPath: d => d.geometry.coordinates,
        getColor: [0, 255, 0],
        getWidth: d => 2 * (d.properties.volume / maxTotalTransfer),
        widthUnits: 'pixels',
        rounded: true,
        extensions: [new PathStyleExtension({ dash: true })],
        getDashArray: [3, 5],
        dashJustified: true,
        pickable: false,
        getTooltip: d => `Transfers: ${d.properties.volume}`,
        updateTriggers: {
            getWidth: maxTotalTransfer
        }
    })
}