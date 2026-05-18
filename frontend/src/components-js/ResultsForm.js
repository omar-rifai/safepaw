import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import { DataContext } from '../App';
import { useContext } from 'react';
import HospitalResourcesChart from './DiagramForm'

export default function ResultsForm() {
  const { outputData } = useContext(DataContext);

  const status = outputData?.status || "";

  return (
    <Box sx={{ minWidth: 275, height: '100%' }}>
      <Card variant="outlined" sx={{ textAlign: 'left', p: 2, mb: 2 }}>
      </Card>
      <Box sx={{ height: '100%' }}  >
        <HospitalResourcesChart />
      </Box>
    </Box>
  );
}
