import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { Card, Grid, Pagination } from '@mui/material';
import { DataContext, UIContext } from '../App';
import { useContext, useState, useMemo } from "react";





export default function HospitalResourcesChart() {

  const [pageCapacity, setPageCapacity] = useState(1)
  const { outputData, inputData } = useContext(DataContext);
  const { selectedFacilityID } = useContext(UIContext);
  const handlePaginateCapacities = (event, value) => {
    setPageCapacity(value)
  };


  const facilities = inputData?.facilities_capacities ?
    outputData?.facilities_loads ? outputData.facilities_loads : inputData.facilities_capacities :
    null

  const ITEMS_PER_PAGE = 3
  const resources = facilities?.[0] ? Object.keys(facilities[0].resources_capacity).sort() : [];
  const paginatedResources = useMemo(() => {

    const start = (pageCapacity - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE

    return resources.slice(start, end);
  }, [resources, pageCapacity]);

  return (
    <div><Pagination count={Math.ceil(resources.length / ITEMS_PER_PAGE)} page={pageCapacity} onChange={handlePaginateCapacities} />
      <Grid container spacing={1} sx={{ justifyContent: "space-evenly", }}>

        {paginatedResources.map(resource => {
          const chartData = facilities.map(f => ({
            facility: f.facility_id,
            capacity: Number(f.resources_capacity?.[resource] ?? 0),
            imported: Number(f.transfers_in?.[resource] ?? 0),
            exported: Number(f.transfers_out?.[resource] ?? 0)
          }));

          return (
            <Card key={resource}>
              <h3>{resource}</h3>

              <ComposedChart width={400} height={300} data={chartData} barCategoryGap="0%"
                barGap={0} interval={0} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="facility" />
                <YAxis width="auto" />
                <Tooltip />
                <Legend />
                <Bar dataKey="capacity" fill="#88adc8ff" />
                <Bar dataKey="imported" fill="#baecb4ff" />
                <Bar dataKey="exported" fill="rgba(248, 98, 98, 0.7)" />
              </ComposedChart>
            </Card>
          );
        })}

      </Grid>
    </div>
  );
}