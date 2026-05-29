import { Grid, Card } from '@mui/material';
import { DataContext } from '../App';
import { useContext } from 'react';
import Dashboard from './diagrams/FacilitiesDiagrams'
import ResourcesChart from './diagrams/ResourcesDiagrams'
import PathwaysChart from './diagrams/PathwaysDiagram'
import ConfigChart from './diagrams/ConfigsDiagrams';
import { Typography } from '@mui/material';

export default function ResultsForm() {
  const { outputData, inputData, activeTab } = useContext(DataContext);

  const status = outputData?.status || "";

  return (
    <Grid sx={{width:"100%",mt:3, ml:2}} >
      {status && <Card sx={{ textAlign: 'left', mb: 2, backgroundColor:"#F9FAFB" }}> <Typography>Status : {status}</Typography> </Card>}
      {Object.keys(inputData).length != 0 &&
        <Grid >
        {activeTab == "tab-facilities" && <Dashboard />}
          {activeTab == "tab-pathways" && <PathwaysChart />}
          {activeTab == "tab-resources" && <ResourcesChart />}
          {activeTab == "tab-instance" && <ConfigChart />}
        </Grid>}
    </Grid>
  );

}
