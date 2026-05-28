import { useState, createContext } from "react";
import { Divider, Box, Button, AppBar, Tabs, Tab, Toolbar, Typography } from '@mui/material';

import InputForm from "./components-js/InputForms";
import ResultsForm from "./components-js/ResultsForm";
import UploadIcon from '@mui/icons-material/Upload';
import { Group, Panel, Separator } from "react-resizable-panels";
import CustomMap from './components-js/Map';
import { styled } from '@mui/material/styles';
import PersonalInjuryIcon from '@mui/icons-material/PersonalInjury';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import RouteIcon from '@mui/icons-material/Route';
import VaccinesIcon from '@mui/icons-material/Vaccines';
import TuneIcon from '@mui/icons-material/Tune';

import "./App.css"

export const DataContext = createContext();
export const UIContext = createContext();
const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});




function App() {

  const [inputData, setInputData] = useState({});
  const [selectedFacilityID, setSelectedFacilityID] = useState(null);
  const [highlightedFacility, setHighlightedFacility] = useState(null);
  const [outputData, setOutputData] = useState({});
  const [activeTab, setActiveTab] = useState("tab-facilities")


  const handleTabChange = (_, val) => {
    setActiveTab(val);
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    const jsonData = JSON.parse(text)
    const response = await fetch("/api/read_file", {
      method: "POST",
      body: JSON.stringify(jsonData),
      headers: { "Content-Type": "application/json" }

    })
    const result = await response.json();
    setInputData(prev => ({
      ...prev,
      ...result
    }));
    setOutputData(null)
  };


  const optimizeInstance = async () => {
    console.log("Calling optimize_instance..")
    const response_convert = await fetch("/api/optimize", {
      method: "POST",
      body: JSON.stringify({ "instance": inputData?.entries?.instance }),
      headers: { "Content-Type": "application/json" }
    })

    const payload = await response_convert.json()
    setOutputData(payload)
  };

  return (
    <DataContext.Provider value={{ inputData, setInputData, outputData, setOutputData, activeTab, setActiveTab }}>
      <UIContext.Provider value={{ selectedFacilityID, setSelectedFacilityID, setHighlightedFacility, highlightedFacility }}>
        <AppBar sx={{ backgroundColor: "#ffffffff" }}>
          <Toolbar sx={{ display: "flex", gap: 4 }}>
            <Box sx={{ minWidth: 500 }}>
              <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto" allowScrollButtonsMobile>
                <Tab label="Facilities" value="tab-facilities" sx={{ fontSize: 10 }} icon={<LocalHospitalIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Pathways" value="tab-pathways" sx={{ fontSize: 10 }} icon={<RouteIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Patient Groups" value="tab-patients" sx={{ fontSize: 10 }} icon={<PersonalInjuryIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Resources" value="tab-resources" sx={{ fontSize: 10 }} icon={<VaccinesIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Model Configuration" value="tab-instance" sx={{ fontSize: 10, maxWidth: 80 }} icon={<TuneIcon sx={{ fontSize: 20 }} />} wrapped />
              </Tabs>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Button variant="outlined" onClick={optimizeInstance} sx={{ flexShrink: 0 }}>Optimize</Button>
            <Button component="label" startIcon={<UploadIcon />} sx={{ flexShrink: 0 }}>  Upload
              <VisuallyHiddenInput type="file" onChange={handleUpload} multiple />
            </Button>
            <Typography variant="h4" sx={{ fontFamily: "'Montserrat', sans-serif", fontWeight: 700, letterSpacing: "0.05em", color: "#333333" }}> SAFEPAW </Typography>
            <Box />
            <Box component="img" src="logo_safepaw.jpg" sx={{ height: 50, width: "auto" }}></Box>
            <Box component="img" src="logo_anr.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_univ-tours.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_emse.png" sx={{ height: 50, width: "auto" }}></Box>

          </Toolbar>
        </AppBar>
        <Divider />
        <Group style={{  height: 900, backgroundColor:"#F9FAFB"}}>
          <Panel  minSize={150} maxSize={550}>
            <Group  orientation="vertical">
              <Panel defaultSize={450} minSize={200} maxSize={700}>
                <InputForm activeTab={activeTab} />
              </Panel>
              <Separator />
              <Panel>
                <ResultsForm />
              </Panel>
            </Group>
          </Panel>
          <Separator />
          <Panel>
            <CustomMap />
          </Panel>
        </Group>
      </UIContext.Provider>
    </DataContext.Provider >
  );
}

export default App;
