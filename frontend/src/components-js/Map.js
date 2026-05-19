import { DeckGL } from '@deck.gl/react';
import { FlyToInterpolator } from '@deck.gl/core';
import { Map } from 'react-map-gl/maplibre';
import { useMemo, useRef, useState, useEffect, useContext } from 'react';
import { getInitializeViewFromGeoJSON, useRegionGeoJSON } from '../utils/mapInitializer';
import { DataContext, UIContext } from "../App";
import { Box, Checkbox, FormGroup, FormControlLabel, Typography } from '@mui/material';
import PatientsTransfersLayer from './map-layers/PatientsTransfersLayer';
import Legend from './map-layers/Legend';
import { RegionFacilityLoadLayer, getRegionFacilityToolTip } from './map-layers/RegionFacilityLoadLayer';
import { FacilityLoadLayer, getFacilityToolTip } from './map-layers/FacilityLoadLayer'
import { FacilityCapacityLayer, getFacilityCapacityToolTip } from './map-layers/FacilityCapacityLayer'


export default function customMap() {

  const { inputData, outputData } = useContext(DataContext);
  const { selectedFacilityID, setSelectedFacilityID} =  useContext(UIContext);
  const containerRef = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 })
  const regions = useMemo(() => outputData?.results?.regions || [], [outputData]);

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

    if (outputData?.results?.list_facility_load && outputData.results.regions) {
      const layer_regionFacilityLoads = RegionFacilityLoadLayer({
        loads: outputData.results.list_facility_load_regions,
        regions: outputData.results.regions,
        selectedItem: selectedFacilityID
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

  useEffect(() => {
    console.log("input data:", inputData);
  }, [inputData]);

  useEffect(() => {
    if (containerRef.current) {
      const { clientWidth, clientHeight } = containerRef.current;
      setSize({ width: clientWidth, height: clientHeight })
    }
  }, []);


  const layers = useMemo(
    () => (output_layers && output_layers.length > 0 ? output_layers : input_layers).filter(Boolean),
    [input_layers, output_layers]
  );

  const renderedLayers = layers.map(layer =>
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
  }, [layers]);

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
            outline: '2px solid #b8b8b9ff',
            boxSizing: 'border-box',
          }}
        >
          <DeckGL
            viewState={viewState}
            onViewStateChange={({ viewState }) => setViewState(viewState)}
            controller={true}
            layers={renderedLayers}
            getTooltip={getTooltip}
            onClick={({ object }) => { if (!object) {
               setSelectedFacilityID(null) ;
              } }}
          >

            <Map
              reuseMaps
              mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
              style={{ width: '100%', height: '100%' }}
              attributionControl={false}
            />

            <Legend inputData={inputData} outputData={outputData} />
          </DeckGL>
        </div>
        {selectedFacilityID&& <Typography>Data filtered for facilitiy {selectedFacilityID}. Click anywhere on the map to unfilter.</Typography>}
      </Box>
    </Box >
  );
}
