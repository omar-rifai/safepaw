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
      <UIContext.Provider value={{deckGLData, setDeckGLData}}>
        <div style={{ padding: 20 }}>
          <h2>SAFEPAW</h2>
          <h3>Optimizing Patients Health Pathways</h3>
          <Divider textAlign="left" sx={{ my: 2 }}>  <Typography variant="body1"> Parameters</Typography> </Divider>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ width: '20%', position: 'relative' }}>
              <InputForm />
            </Box>
            <Box sx={{ width: '40%', position: 'relative' }}>
              <CustomMap inputData={inputData} outputData={outputData} />
            </Box>
            <Box sx={{ width: '40%', position: 'relative' }}>
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
