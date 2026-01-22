
import bbox from '@turf/bbox';
import { WebMercatorViewport } from '@deck.gl/core';
import { useState, useEffect } from 'react'


export function getInitializeViewFromGeoJSON(geojson, width = 800, height = 600, padding = 20) {

    if (!geojson || !geojson.features?.length) {
        return { longitude: 2.5, latitude: 46.7, zoom: 5, pitch: 0, bearing: 0 };
    }

    const bounds = bbox(geojson);
    const viewport = new WebMercatorViewport({ width, height });
    const { longitude, latitude, zoom } = viewport.fitBounds([
        [bounds[0], bounds[1]],
        [bounds[2], bounds[3]],
    ], { padding });

    return { longitude, latitude, zoom, pitch: 0, bearing: 0 };
}

export function useRegionGeoJSON(regionName) {

    const [regionGeoJSON, setRegionGeoJSON] = useState(null)

    useEffect(() => {
        fetch("data/regions.geojson")
            .then(res => res.json())
            .then(data => {
                const features = data.features.filter(feature => feature.properties.nom == regionName);
                setRegionGeoJSON({type: "FeatureCollection", features})
            });
    }, [regionName]);


    return regionGeoJSON
}