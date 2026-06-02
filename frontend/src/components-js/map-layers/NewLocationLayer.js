import { ScatterplotLayer } from '@deck.gl/layers';
import { hexToRgb, rgbToHex } from '@mui/material';

export function newLocationLayer(pickedLocation, animationFrame, setAnimationFrame) {

    if (!pickedLocation) {
        console.log("no picked location unfortuntaly")
        return
    }

    setInterval(()=> setAnimationFrame(!animationFrame), 500 )

    console.log("there is a picked location!")
    return new ScatterplotLayer({
        id: 'temp-location',
        data: [pickedLocation],
        getPosition: d => [d.lon, d.lat],
        getFillColor: [40,200, 100, 130],
        getRadius: animationFrame && pickedLocation? 15:0,
        radiusScale:1,
        getLineColor: [255, 255, 255, 180],
        lineWidthMinPixels: 2,
        transitions: {getRadius:50},
        radiusUnits: 'pixels',
    });
}


