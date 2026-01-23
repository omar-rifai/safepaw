import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import { DataContext } from '../App';
import { useContext } from 'react';
import HospitalResourcesChart from './DiagramForm'

export default function ResultsForm() {
  const { outputData} = useContext(DataContext);

  if (!outputData || !Object.keys(outputData).length) return <Typography>No results to display.</Typography>;

  const { status, obj_val } = outputData;

  console.log("outputData in ResultForm: ", outputData)

  return (
    <Box sx={{ minWidth: 275, height: '100%' }}>
      <Card variant="outlined" sx={{ textAlign: 'left', p: 2, mb: 2 }}>
        <Typography><strong>Status:</strong> {status}</Typography>
        <Typography><strong>Objective:</strong> {obj_val}</Typography>
      </Card>
      <Box  sx={{height: '100%'}}  >
        <HospitalResourcesChart/>
      </Box>
    </Box>
  );
}
