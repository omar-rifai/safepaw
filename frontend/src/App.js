import { useState, useEffect, createContext, useId } from "react";
import { Box, AppBar, Toolbar, Typography, } from '@mui/material';

import DataGridForm from "./components-js/TabsForm";
import ResultsForm from "./components-js/ResultsForm";
import { Group, Panel, Separator } from "react-resizable-panels";
import CustomMap from './components-js/Map';
import ToolbarForm from "./components-js/ToolbarForm"


import "./App.css"

export const DataContext = createContext();
export const UIContext = createContext();




function App() {

  const [inputData, setInputData] = useState({});
  const [selectedFacilityID, setSelectedFacilityID] = useState(null);
  const [selectedPathwayID, setSelectedPathwayID] = useState(null)
  const [highlightedFacility, setHighlightedFacility] = useState(null);
  const [pickedLocation, setPickedLocation] = useState(null);
  const [isPickingLocation, setIsPickingLocation] = useState(false);
  const [outputData, setOutputData] = useState({});
  const [activeTab, setActiveTab] = useState("tab-facilities")


  useEffect(() => {
    async function loadState() {
      const res = await fetch("/api/state");
      const data = await res.json()
      setInputData(data)
    }
    loadState()
  }, []);



  return (
    <DataContext.Provider value={{ inputData, setInputData, outputData, setOutputData, activeTab, setActiveTab, selectedPathwayID, setSelectedPathwayID }}>
      <UIContext.Provider value={{ selectedFacilityID, setSelectedFacilityID, setHighlightedFacility, highlightedFacility, isPickingLocation, setIsPickingLocation, pickedLocation, setPickedLocation }}>
        <AppBar sx={{ backgroundColor: "#fff", color: "#000" }}>
          <Toolbar sx={{ display: "flex", gap: 4 }}>
            <Typography variant="h4" sx={{ fontFamily: "'Montserrat', sans-serif", fontWeight: 700, letterSpacing: "0.05em", color: "#333333", mr: 10 }}> SAFEPAW </Typography>
            <ToolbarForm />
            <Box flexGrow={1} />
            <Box component="img" src="logo_safepaw.jpg" sx={{ height: 50, width: "auto" }}></Box>
            <Box component="img" src="logo_anr.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_univ-tours.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_emse.png" sx={{ height: 50, width: "auto" }}></Box>

          </Toolbar>
        </AppBar>

        <Group style={{ height:"100svh" }}>
          <Panel defaultSize={550} minSize={400} maxSize={750}>
            <Group orientation="vertical" >
              <Panel defaultSize={600} minSize={200} maxSize={700}>
                <DataGridForm activeTab={activeTab} setActiveTab={setActiveTab} />
              </Panel>
              <Separator style={{ height: "2px", minHeight: "2px", backgroundColor: "#c8cdd6ff", cursor: "row-resize", flexShrink: 0 }} />
              <Panel>
                {inputData.entries && <ResultsForm />}
              </Panel>
            </Group>
          </Panel>
          <Separator style={{ width: "2px", backgroundColor: "#c8cdd6ff", cursor: "row-resize", flexShrink: 0 }} />

          <Panel  style={{ overflow: "hidden" }}>
            <CustomMap />
          </Panel>

        </Group>
      </UIContext.Provider>
    </DataContext.Provider >
  );
}

export default App;
