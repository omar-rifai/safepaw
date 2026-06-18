import { DeckGL } from '@deck.gl/react';
import { FlyToInterpolator } from '@deck.gl/core';
import { Map } from 'react-map-gl/maplibre';
import { useMemo, useRef, useState, useEffect, useContext } from 'react';
import { getInitializeViewFromGeoJSON } from '../utils/mapInitializer';
import { DataContext, UIContext } from "../App";
import { Box, Checkbox, FormGroup, FormControlLabel, Typography } from '@mui/material';
import PatientsTransfersLayer from './map-layers/PatientsTransfersLayer';
import Legend from './map-layers/Legend';
import { RegionFacilityLoadLayer, getRegionFacilityToolTip } from './map-layers/RegionFacilityLoadLayer';
import { FacilityLoadLayer, getFacilityToolTip } from './map-layers/FacilityLoadLayer'
import { FacilityCapacityLayer, getFacilityCapacityToolTip } from './map-layers/FacilityCapacityLayer'
import { HighlightLayer } from './map-layers/HighlightLayer';
import { newLocationLayer } from './map-layers/NewLocationLayer';

export default function customMap() {

  const { inputData, outputData } = useContext(DataContext);
  const { selectedFacilityID, setSelectedFacilityID, pickedLocation, setPickedLocation, setIsPickingLocation, isPickingLocation } = useContext(UIContext);
  const containerRef = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 })
  const [animationFrame, setAnimationFrame] = useState(0)
  const regions = useMemo(() => outputData?.results?.regions || [], [outputData]);

  const selectedInfo = inputData.entries?.facilities?.find((e) => e.facility_id == selectedFacilityID)

  const regionGeoJSON = inputData?.bbox;
  const [viewState, setViewState] = useState({
    longitude: 2.5,
    latitude: 46.7,
    zoom: 5,
    pitch: 0,
    bearing: 0
  })

  const [visibleLayers, setVisibleLayers] = useState({});

  useEffect(() => {
    let raf;
    if (!pickedLocation) return;
    const animate = () => {
      setAnimationFrame(f => f + 1);
      raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [pickedLocation]);


  useEffect(() => {
    if (!regionGeoJSON) return;
    const newView = getInitializeViewFromGeoJSON(regionGeoJSON, size.width, size.height);
    setViewState({
      ...newView,
      transitionDuration: 1000,
      transitionInterpolator: new FlyToInterpolator(),
    });
  }, [regionGeoJSON, size.width, size.height]);

  const tooltipMap = {
    "facilities-volume": getFacilityToolTip,
    "facilities-capacity": getFacilityCapacityToolTip,
    "region-to-facility": getRegionFacilityToolTip
  };

  function getTooltip(info) {
    if (!info.object) return null;

    const fn = tooltipMap[info.layer.id];
    return fn ? fn(info, regions) : null;
  }

  const output_layers = useMemo(() => {

    const list_layers = []

    if (outputData?.facilities_loads) {
      const layer_facilityLoads = FacilityLoadLayer({
        loads: outputData.facilities_loads,
        selectedFacilityID: selectedFacilityID,
        setSelectedFacilityID: setSelectedFacilityID,
      });
      list_layers.push(layer_facilityLoads)
    }

    if (outputData?.facilities_regions_loads) {

      const layer_regionFacilityLoads = RegionFacilityLoadLayer({
        loads: outputData.facilities_regions_loads,
        selectedFacilityID: selectedFacilityID
      });
      list_layers.push(layer_regionFacilityLoads)
    }


    if (outputData?.results?.list_patient_transfers) {
      const layer_patientsTransfers = PatientsTransfersLayer({
        transfers: outputData.results.list_patient_transfers,
      });
      list_layers.push(layer_patientsTransfers)
    }

    return list_layers;
  }, [outputData, selectedFacilityID]);


  const input_layers = useMemo(() => {

    const list_layers = []

    if (inputData?.facilities_capacities) {
      const layer_facilityLoads = FacilityCapacityLayer({
        facilities: inputData.facilities_capacities || [],
        selectedFacilityID: selectedFacilityID,
        setSelectedFacilityID: setSelectedFacilityID
      });
      list_layers.push(layer_facilityLoads)
    }


    return list_layers;

  }, [inputData, inputData.facilities_capacities, selectedFacilityID]);


  const highlightLayer = useMemo(()=> {
    if (selectedFacilityID == null) return null;
    
    return HighlightLayer({
      facilities: inputData?.facilities_capacities || [],
      selectedFacilityID
    });
  },[inputData, selectedFacilityID])


  useEffect(() => {
    console.log("input data:", inputData);
  }, [inputData]);


  const newLocLayer = pickedLocation ? newLocationLayer(pickedLocation, animationFrame) : null;

  useEffect(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current;
      setSize({ width: clientWidth, height: clientHeight })
    }
  }, []);


  const layers = useMemo(
    () => [...(output_layers?.length > 0 ? output_layers : input_layers),
           highlightLayer].filter(Boolean),
    [input_layers, output_layers, highlightLayer]
  );

  const renderedLayers = [...layers, newLocLayer].filter(Boolean).map(layer =>
    layer.clone({
      visible: visibleLayers[layer.id] !== false
    })
  );


  useEffect(() => {
    if (layers.length > 0) {
      setVisibleLayers(prev =>
        layers.reduce(
          (acc, layer) => layer?.id && !(layer.id in acc) ?
            { ...acc, [layer.id]: true } : acc,
          { ...prev }
        ));
    }
  }, [input_layers, output_layers]);

  return (
    <Box sx={{ height: "100%" }} ref={containerRef} >
      {false &&
        <FormGroup row>
          {
            layers.map((layer, i) => (
              <FormControlLabel
                key={layer.id}
                control=
                {
                  <Checkbox
                    checked={!!visibleLayers[layer.id]}
                    onChange={(e) =>
                      setVisibleLayers(prev => ({
                        ...prev,
                        [layer.id]: e.target.checked,
                      }))
                    }
                  />
                }
                label={layer?.id}>
              </FormControlLabel>))
          }
        </FormGroup>
      }
      <Box sx={{ height: "100%", position: "relative" }} >
        <div
          style={{
            width: '100%',
            height: '100%',
          }}
        >
          <DeckGL viewState={viewState} onViewStateChange={({ viewState }) => setViewState(viewState)} controller={true} layers={renderedLayers} getTooltip={getTooltip}
            //getCursor={({ isPickingLocation }) => isPickingLocation ? 'crosshair' : undefined}
            onClick={(info) => {
              console.log("on click:", info.coordinate, isPickingLocation)
              if (isPickingLocation) {
                const [lon, lat] = info.coordinate;
                const newLoc = { lat, lon };
                setPickedLocation(newLoc);
                setIsPickingLocation(false);
                return;
              }
              if (!info.object) {
                setSelectedFacilityID(null);
              }
            }}
          >

            <Map
              reuseMaps
              mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
              style={{ width: '100%', height: '100%' }}
              attributionControl={false}
            />

            <Legend inputData={inputData} outputData={outputData} />
          </DeckGL>
        </div>
        {selectedInfo?.info &&
          <Box
            sx={{
              position: "absolute",
              top: 100,
              right: 20,
              zIndex: 1000,
              bgcolor: "white",
              p: 2,
              borderRadius: 2,
              boxShadow: 3,
              minWidth: 250,
              backgroundColor: "transparent",
            }}
          >
            <Typography>
              {selectedInfo?.info?.liblongcategetab}
            </Typography>
            <Typography>
              {selectedInfo?.info?.rslongue}
            </Typography>
            <Typography>
              N° finess {selectedFacilityID ?? ""}
            </Typography>
            {selectedInfo?.info?.siret &&
              <Typography>
                N° siret: {selectedInfo?.info?.siret}
              </Typography>
            }
            {selectedInfo?.info?.codepostal &&
              <Typography>
                voie {selectedInfo?.info?.voie} {selectedInfo?.info?.codepostal}
              </Typography>
            }
            {selectedInfo?.info?.liblongmft &&
              <Typography>
                MFT: {selectedInfo?.info?.liblongmft}
              </Typography>
            }

          </Box>
        }
      </Box>
    </Box>
  );
}
