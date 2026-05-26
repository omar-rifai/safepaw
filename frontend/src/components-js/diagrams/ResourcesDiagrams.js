import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, ReferenceLine } from "recharts";
import { Card, Box, Tabs, Tab, Stack, Typography } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext, useState, useMemo, useRef } from "react";


export default function ResourcesChart() {

  const [activeResource, setActiveResource] = useState(null)
  const { outputData, inputData } = useContext(DataContext);
  const { selectedFacilityID } = useContext(UIContext);

  console.log("in resource diagram outputdata", outputData)

  const facilities_capacities = inputData?.facilities_capacities ?? null;
  const facilities_loads = outputData?.facilities_loads ?? null

  const resources = useMemo(() => {
    return facilities_capacities?.[0]
      ? Object.keys(facilities_capacities[0].resources_capacity).sort()
      : [];
  }, [facilities_capacities, facilities_loads]);

  const currentResource = useMemo(() =>
    activeResource ?? resources[0], [activeResource]
  );

  const chartInputData = useMemo(() => {
    const loadsMap = new Map(facilities_loads?.map(f => [f.facility_id, f]))
    return facilities_capacities.map(f => {
      const out = loadsMap.get(f.facility_id)
      return {
        facility: f.facility_id,
        capacity: Number(f.resources_capacity?.[currentResource] ?? 0),
        imported: Number(out?.transfers_in?.[currentResource] ?? 0),
        exported: Number(out?.transfers_out?.[currentResource] ?? 0)
      }
    })
  }, [facilities_capacities, currentResource])


  const chartOutputData = useMemo(() =>
    facilities_loads?.map(f => ({
      facility: f.facility_id,
      usage: Number(f.usage?.[currentResource] ?? 0).toFixed(2),
    })) ?? [],
    [facilities_loads, currentResource]);


  return (
    <Stack direction="row" alignItems="center" gap={3} >

      {inputData && <ResourcesInputChart resources={resources} currentResource={currentResource}
        chartData={chartInputData} selectedFacilityID={selectedFacilityID} setActiveResource={setActiveResource} />}
      {outputData && <ResourcesOutputChart resources={resources} currentResource={currentResource}
        chartData={chartOutputData} selectedFacilityID={selectedFacilityID} setActiveResource={setActiveResource} />}

    </Stack >

  );
}


function ResourcesInputChart({ resources, currentResource, chartData, selectedFacilityID, setActiveResource }) {

  const { outputData } = useContext(DataContext);
  return (

    <Card sx={{ width: 650, height: "auto" }}>
      <Typography sx={{ pl: "10%", fontFamily: "Roboto" }}> Resource Capacity per Facility</Typography>
      <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>
        <Tabs value={currentResource} onChange={(_, v) => setActiveResource(v)} orientation="vertical" variant="scrollable" scrollButtons="auto"
          sx={{ height: 400, overflowY: "auto" }}>
          {resources.map(r => <Tab key={r} value={r} label={r}></Tab>)}
        </Tabs>
        <ResponsiveContainer width="100%" height={400} style={{ flex: 1, minWidth: 0 }}>
          <ComposedChart data={chartData}
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
  )
}



function ResourcesOutputChart({ resources, currentResource, chartData, selectedFacilityID, setActiveResource }) {
  return (

    <Card sx={{ width: 650, height: "auto" }}>
      <Typography sx={{ pl: "10%", fontFamily: "Roboto" }}> Resource Usage per Facility</Typography>
      <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>
        <Tabs value={currentResource} onChange={(_, v) => setActiveResource(v)} orientation="vertical" variant="scrollable" scrollButtons="auto"
          sx={{ height: 400, overflowY: "auto" }}>
          {resources.map(r => <Tab key={r} value={r} label={r}></Tab>)}
        </Tabs>
        <ResponsiveContainer width="100%" height={400} style={{ flex: 1, minWidth: 0 }}>
          <ComposedChart data={chartData}
            margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>
            <Tooltip />

            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="facility" padding={{ left: 30, right: 30 }} />
            <YAxis width="auto" />
            <Legend />
            <ReferenceArea x1={selectedFacilityID} x2={selectedFacilityID} fill="#88adc8ff" fillOpacity={0.3} />
            <Bar stackId="a" dataKey="usage" fill="#ab9dbdff" />
          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Card>
  )
}
