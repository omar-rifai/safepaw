import { useState, createContext } from "react";
import { Divider, Typography, Box } from '@mui/material';

import InputForm from "./components-js/InputForms";
import DashboardForm from "./components-js/DashboardForm";
import ResultsForm from "./components-js/ResultsForm";
import CustomMap from './components-js/Map';
import "./App.css"

export const DataContext = createContext();
export const UIContext = createContext();

function App() {

  const [inputData, setInputData] = useState({});
  const [outputData, setOutputData] = useState({});
  const [deckGLData, setDeckGLData] = useState({});

  return (
    <DataContext.Provider value={{ inputData, setInputData, outputData, setOutputData }}>
      <UIContext.Provider value={{ deckGLData, setDeckGLData }}>
        <div style={{ padding: 20 }}>
          <Box
            sx={{
              display: "flex", alignItems: "center", justifyContent: "center", gap: 2,
              padding: "8px 16px", backgroundColor: "#f2f4f6ff", color: "black", 
            }}>
            <Box component="img" src="logo_safepaw.jpg" sx={{ height: 50, width: "auto", ml: -40 }}></Box>
            <Typography variant="h4" sx={{
              mx: 2, fontFamily: "'Montserrat', sans-serif", fontWeight: 700,
              letterSpacing: "0.05em", color: "#333333"
            }}>SAFEPAW</Typography>
            <Box component="img" src="logo_anr.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_univ-tours.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_emse.png" sx={{ height: 50, width: "auto" }}></Box>
          </Box>
          <Divider textAlign="left" sx={{ my: 2, '&::before': { width: '5%' }  }}>  <Typography variant="body1"> France's Maternity Facilities</Typography> </Divider>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'stretch', height: 600 }}>
            <Box sx={{ width: '20%', position: 'relative' }}>
              <InputForm />
            </Box>
            <Box sx={{ width: '40%', height: '100%', position: 'relative' }}>
              <CustomMap inputData={inputData} outputData={outputData} />
            </Box>
            <Box sx={{ width: '40%', height: '100%', position: 'relative' }}>
              <DashboardForm
                inputData={inputData}
              />
              <Divider textAlign="left" sx={{ my: 2 }}> <Typography variant="body1"> Results </Typography>  </Divider>
              <ResultsForm outputData={outputData} />
            </Box>
          </Box>

        </div >
      </UIContext.Provider>
    </DataContext.Provider>
  );
}

export default App;
