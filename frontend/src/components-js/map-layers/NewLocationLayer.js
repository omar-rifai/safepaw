import { ScatterplotLayer } from '@deck.gl/layers';

export function newLocationLayer(pickedLocation, animationFrame) {

    if (!pickedLocation) {
        return
    }

    const pulse = (Math.sin(animationFrame * 0.1) + 1)

    return new ScatterplotLayer({
        id: 'temp-location',
        data: [pickedLocation],
        getPosition: d => [d.lon, d.lat],
        getFillColor: [40,200, 200, 100],
        getRadius: 6 + pulse*5,
        radiusScale:1,
        getLineColor: [255, 255, 255, 180],
        lineWidthMinPixels: 2,
        radiusUnits: 'pixels',
        updateTriggers: {getRadius: animationFrame}
    });
}


