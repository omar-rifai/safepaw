import { Grid, Card } from '@mui/material';
import { DataContext } from '../App';
import { useContext } from 'react';
import Dashboard from './diagrams/FacilitiesDiagrams'
import ResourcesChart from './diagrams/ResourcesDiagrams'
import PathwaysChart from './diagrams/PathwaysDiagram'
import PatientsChart from './diagrams/PatientsDiagrams';
import ConfigChart from './diagrams/ConfigsDiagrams';
import { Typography } from '@mui/material';

export default function ResultsForm() {
  const { outputData, inputData, activeTab } = useContext(DataContext);

  const status = outputData?.status || "";

  return (
    <Grid sx={{width:"100%",mt:3, ml:10}} >
      {status && <Card variant="outlined" sx={{ textAlign: 'left', p: 2, mb: 2 }}> <Typography>Status : {status}</Typography> </Card>}
      {Object.keys(inputData).length != 0 &&
        <Grid sx={{width:"100%"}} >
        {activeTab == "tab-facilities" && <Dashboard />}
          {activeTab == "tab-pathways" && <PathwaysChart />}
          {activeTab == "tab-resources" && <ResourcesChart />}
          {activeTab == "tab-patients" && <PatientsChart />}
          {activeTab == "tab-instance" && <ConfigChart />}
        </Grid>}
    </Grid>
  );

}
