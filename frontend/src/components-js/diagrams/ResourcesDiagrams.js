import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, useActiveTooltipDataPoints } from "recharts";
import { Card, Box, Tabs, Tab, Stack } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext, useState, useMemo } from "react";


export default function ResourcesChart() {

  const [activeResource, setActiveResource] = useState(null)
  const { outputData, inputData } = useContext(DataContext);
  const { selectedFacilityID, setSelectedFacilityID } = useContext(UIContext);

  console.log("in resource diagram outputdata", outputData)

  const facilities_capacities = inputData?.facilities_capacities ?? [];
  const facilities_loads = outputData?.facilities_loads ?? []

  const resources = useMemo(() => {
    return facilities_capacities?.[0]
      ? Object.keys(facilities_capacities[0].resources_capacity).sort()
      : [];
  }, [facilities_capacities, facilities_loads]);

  const currentResource = useMemo(() =>
    activeResource ?? resources[0], [activeResource, inputData]
  );

  const chartInputData = useMemo(() => {
    const loadsMap = new Map(facilities_loads?.map(f => [f.facility_id, f]))
    return facilities_capacities.map(f => {
      const out = loadsMap.get(f.facility_id)
      return {
        facility: f.facility_id,
        capacity: Number(f.resources_capacity?.[currentResource] ?? 0),
        imported: Number(out?.transfers_in?.[currentResource] ?? 0),
        exported: Number(out?.transfers_out?.[currentResource] ?? 0),
        usage: Number(out?.usage?.[currentResource] * Number(f.resources_capacity?.[currentResource]- Number(out?.transfers_out?.[currentResource] ?? 0)+  Number(out?.transfers_in?.[currentResource] ?? 0))).toFixed(0)
          ?? 0,
      }
    })
  }, [facilities_capacities, facilities_loads, currentResource])



  return (
    <Stack alignItems="center" gap={3} >

      {inputData && <ResourcesInputChart resources={resources} currentResource={currentResource} setSelectedFacilityID={setSelectedFacilityID}
        chartData={chartInputData} selectedFacilityID={selectedFacilityID} setActiveResource={setActiveResource} />}
    </Stack >

  );
}


function ResourcesInputChart({ resources, currentResource, chartData, selectedFacilityID, setActiveResource, setSelectedFacilityID }) {

  const { outputData } = useContext(DataContext);
  return (

    <Card sx={{ width: "90%", height: "auto" }}>
      <Box sx={{ width: "100%", height: "100%" }}>
        <Tabs value={currentResource} onChange={(_, v) => setActiveResource(v)} orientation="horizontal" variant="scrollable" scrollButtons="auto"
          sx={{ overflowX: "auto" }}>
          {resources.map(r => <Tab key={r} value={r} label={r}></Tab>)}
        </Tabs>
        <ResponsiveContainer width="100%" height={300} style={{ flex: 1, minWidth: 0 }}>
          <ComposedChart data={chartData} 
           onClick={(e)=>{setSelectedFacilityID(e.activeLabel ?? null)}}
            margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>
            <Tooltip />

            <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.5} />
            <XAxis dataKey="facility" padding={{ left: 30, right: 30 }} />
            <YAxis width="auto" />
            <Legend />
            <ReferenceArea x1={selectedFacilityID} x2={selectedFacilityID} fill="#7eb6eb9f" radius={outputData ? [0, 0, 0, 0] : [6, 6, 0, 0]} />
            <Bar barSize={30} stackId="a" dataKey="capacity" fill="#759bc9ff" />
            {outputData && (<>
              <Bar stackId="a" dataKey="imported" fill="#baecb4ff" radius={[6, 6, 0, 0]} />
              <Bar stackId="a" dataKey="exported" fill="rgba(248, 98, 98, 0.7)" radius={[6, 6, 0, 0]} />
              <Bar barSize={30} dataKey="usage" fill="#ab9dbdff" radius={[6, 6, 0, 0]} />
            </>)}
          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Card>
  )
}

