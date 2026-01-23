import {
  ComposedChart,
  Line,
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
      capacity: f.properties?.capacities[0] - f.properties?.transfers_out[0],
      load : Math.round(f.properties?.load*4.6),
      imported: f.properties?.transfers_in[0],
      exported: f.properties?.transfers_out[0]
   }));

  return (
    <ComposedChart
      width={600}
      height={300}
      data={facilities_data}
      margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="resource" tick={false} />
      <YAxis width="auto" />
      <Tooltip />
      <Legend />
      <Bar dataKey="capacity" stackId="a" fill="#88adc8ff" />
      <Bar dataKey="imported" stackId="a" fill="#baecb4ff" />
      <Bar dataKey="exported" stackId="a" fill="rgba(248, 98, 98, 0.7)" />

      <Line type="monotone" dataKey="load" fill="#052e34ff" />

    </ComposedChart>
  );
}