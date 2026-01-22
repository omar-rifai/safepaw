import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { DataContext, UIContext } from '../App';
import { useContext } from "react";


export default function HospitalResourcesChart() {

  const { outputData } = useContext(DataContext);
  const { deckGLData } = useContext(UIContext);

  console.log("in Diagram, object selected:", deckGLData)

  const filtered_output = deckGLData.properties?.facility_id ?
    outputData.list_facility_load?.filter(item => item.properties.facility_id == deckGLData.properties?.facility_id)
    : outputData.list_facility_load;

  const facilities_data = filtered_output.flatMap(f =>
   ({
      resource: f.properties.facility_id,
      capacity: f.properties?.capacities[0],
      imported: f.properties?.transfers_in[0],
      exported: f.properties?.transfers_out[0]
   }));

  return (
    <BarChart
      width={600}
      height={300}
      data={facilities_data}
      margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="resource" tick={false} />
      <YAxis dataKey="capacity" />
      <Tooltip />
      <Legend />

      {/* Base capacity */}
      <Bar dataKey="capacity" stackId="a" fill="#88adc8ff" />

      {/* Imported stacked on top */}
      <Bar dataKey="imported" stackId="a" fill="#baecb4ff" />

      {/* Exported stacked on top (semi-transparent) */}
      <Bar dataKey="exported" stackId="a" fill="rgba(248, 98, 98, 0.7)" />
    </BarChart>
  );
}
