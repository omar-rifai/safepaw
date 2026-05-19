import { Stack, Card } from '@mui/material';
import { DataContext } from '../App';
import { useContext } from 'react';
import ResourcesChart from './DiagramForm'
import { Typography } from '@mui/material';

export default function ResultsForm() {
  const { outputData } = useContext(DataContext);

  const status = outputData?.status || "";

  return (
    <Stack sx={{ width: '40%'  }}>
      {status && <Card variant="outlined" sx={{ textAlign: 'left', p: 2, mb: 2 }}> <Typography>Status : {status}</Typography> </Card>}
      <Card style={{ flex: 1, minWidth: 0, height: "100%" }}>
        <ResourcesChart />
      </Card>
    </Stack>
  );
  
}
