import { useState, createContext } from "react";
import { Divider, Box, Button, Grid, Stack, AppBar, Toolbar, Typography } from '@mui/material';

import InputForm from "./components-js/InputForms";
import ResultsForm from "./components-js/ResultsForm";
import UploadIcon from '@mui/icons-material/Upload';
import AddIcon from '@mui/icons-material/Add';
import CustomMap from './components-js/Map';
import { styled } from '@mui/material/styles';
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
  const [outputData, setOutputData] = useState({});
  const [deckGLData, setDeckGLData] = useState({});

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
    setInputData(result);
    setOutputData(null)
  };


  const optimizeInstance = async () => {
    console.log("Calling optimize_instance..")
    if (!Object.hasOwn(inputData, "instance")) {

      console.log("no input data instance for optimization")
      return;
    }
    const response_convert = await fetch("/api/optimize", {
      method: "POST",
      body: JSON.stringify({"data":inputData.instance, steps:{"preprocess":true, "optimize":true, "postprocess":true}}),
      headers: { "Content-Type": "application/json" }
    })

    const payload = await response_convert.json()
    setOutputData(payload)
    console.log(payload)
  };

  return (
    <DataContext.Provider value={{ inputData, setInputData, outputData, setOutputData }}>
      <UIContext.Provider value={{ deckGLData, setDeckGLData }}>
        <AppBar sx={{ backgroundColor: "#ffffffff" }}>
          <Toolbar sx={{
            display: "flex", justifyContent: "center", gap: 4
          }}>
            <Typography variant="h4"
              sx={{
                fontFamily: "'Montserrat', sans-serif", fontWeight: 700,
                letterSpacing: "0.05em", color: "#333333"
              }}>
              SAFEPAW
            </Typography>
            <Button
              component="label"
              startIcon={<UploadIcon />}>
              Upload
              <VisuallyHiddenInput
                type="file"
                onChange={handleUpload}
                multiple
              />
            </Button>
            <Button startIcon={<AddIcon />} >
              Create
            </Button>
            <Box sx={{ flexGrow: 1 }} />
            <Box component="img" src="logo_safepaw.jpg" sx={{ height: 50, width: "auto" }}></Box>
            <Box component="img" src="logo_anr.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_univ-tours.png" sx={{ height: 30, width: "auto" }}></Box>
            <Box component="img" src="logo_emse.png" sx={{ height: 50, width: "auto" }}></Box>

          </Toolbar>
        </AppBar>
        <Divider />

        <Stack sx={{ mt: 15 }} spacing={2}>
          <Grid container spacing={5} sx={{ justifyContent: "space-evenly", alignItems: "center" }}>
            <Grid size={8} sx={{ width: 500 }}>
              <InputForm />
              <Grid
                container
                sx={{ mt: 2, display: "flex", justifyContent: "end" }} >
                <Button variant="outlined" onClick={optimizeInstance}>Optimize</Button>
              </Grid>
            </Grid>
            <Grid size={7} sx={{ minWidth: 550, height: 600 }}>
              <CustomMap />
            </Grid>
          </Grid>

          <Box sx={{ width: '100%', height: '100%' }}>
            <Divider sx={{ mt: 8 }} />
            <ResultsForm />
          </Box>
        </Stack>
      </UIContext.Provider>
    </DataContext.Provider >
  );
}

export default App;
