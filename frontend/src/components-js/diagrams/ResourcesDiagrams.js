import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, ReferenceLine } from "recharts";
import { Card, Box, Tabs, Tab, Grid, Typography} from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext, useState, useMemo, useRef } from "react";


export default function ResourcesChart() {

  const [activeResource, setActiveResource] = useState(null)
  const { outputData, inputData } = useContext(DataContext);
  const { selectedFacilityID } = useContext(UIContext);

  const chartRef = useRef(null);

  const facilities = inputData?.facilities_capacities ?
    outputData?.facilities_loads ? outputData.facilities_loads : inputData.facilities_capacities :
    null

  const resources = useMemo(() => {
    return facilities?.[0]
      ? Object.keys(facilities[0].resources_capacity).sort()
      : [];
  }, [facilities]);

  const currentResource = activeResource ?? resources[0];
  const chartData = facilities?.map(f => ({
    facility: f.facility_id,
    capacity: Number(f.resources_capacity?.[currentResource] ?? 0),
    imported: Number(f.transfers_in?.[currentResource] ?? 0),
    exported: Number(f.transfers_out?.[currentResource] ?? 0)
  })) ?? [];


  return (
    <Grid sx={{ width: 800 }}>
      <Card sx={{ width: "100%", mx: "auto", mt: 10 }}>
        <Typography sx={{pl:"10%", fontFamily: "Roboto" }}> Resource Capacity per Facility</Typography>
        <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>
          <Tabs value={currentResource} onChange={(_, v) => setActiveResource(v)} orientation="vertical" variant="scrollable" scrollButtons="auto"
            sx={{ height: 400, overflowY: "auto" }}>
            {resources.map(r => <Tab key={r} value={r} label={r}></Tab>)}
          </Tabs>


          <ResponsiveContainer width="100%" height={400} style={{ flex: 1, minWidth: 0 }}>
            <ComposedChart data={chartData} ref={chartRef}
              margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>
              <Tooltip />

              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="facility" padding={{ left: 30, right: 30 }} />
              <YAxis width="auto" />
              <Legend />
              <ReferenceArea x1={selectedFacilityID} x2={selectedFacilityID} fill="#88adc8ff" fillOpacity={0.3} />
              <Bar stackId="a" dataKey="capacity" fill="#88adc8ff" />
              {outputData && (<>
                <Bar stackId="a" dataKey="imported" fill="#baecb4ff" />
                <Bar stackId="a" dataKey="exported" fill="rgba(248, 98, 98, 0.7)" />)
              </>)}
            </ComposedChart>
          </ResponsiveContainer>
        </Box>
      </Card>
    </Grid>

  );
}