
import { Stack, Grid } from '@mui/material';
import { DataContext } from '../../App';
import { useContext } from "react";
import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, } from "recharts";
import { UIContext } from '../../App';



export default function FacilitiesDiagrams() {

  const { inputData } = useContext(DataContext);
  const { selectedFacilityID } = useContext(UIContext);

  const pathways = inputData?.entries?.pathways ?? [];

  const pathways_unique = pathways.filter((obj1, i, arr) =>
    arr.findIndex(obj2 => ['facility_id', 'pathway_id'].every(key => obj2[key] === obj1[key])
    ) === i
  )

  const groups = inputData?.entries?.patients_groups ?? [];

  const patientsGroupsChartData = Object.values(
    (groups??[]).reduce((acc, { group_id }) => {
      acc[group_id] ??= { group_id, n_facilities: 0 };
      acc[group_id].n_facilities++;
      return acc;
    }, {})
  );


  const pathwaysChartData = Object.values(
    (pathways_unique??[]).reduce((acc, { pathway_id }) => {
      acc[pathway_id] ??= { pathway_id, n_facilities: 0 };
      acc[pathway_id].n_facilities++;
      return acc;
    }, {})
  );

  const selectedPathways = pathways_unique.filter((e) => e.facility_id === selectedFacilityID)
    .map((e) => e.pathway_id);





  return (
    <Stack  alignItems="left">
      <Grid container sx={{ width: "95%", height: 300 }}>

        <ResponsiveContainer width="100%" height="100%" style={{ flex: 1, minWidth: 0, background: "#fff", borderRadius: 2, p: 1 }}>
          <ComposedChart data={pathwaysChartData} barCategoryGap="20%" margin={{ top: 30, right: 30, bottom: 50, left: 0 }}>

            <Tooltip />

            <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.5} />
            <XAxis dataKey="pathway_id" type="category" tickMargin={10} label={{ value: "Pathway ID", position: "bottom", offset: 10 }} />
            <YAxis type="number" allowDecimals={false} label={{value: "Number of occurences", offset:5, angle:-90}} />
            {selectedPathways.length > 0 && (<ReferenceArea y1={selectedPathways[0]} y2={selectedPathways[selectedPathways.length - 1]}
              fill="#88adc8ff" fillOpacity={0.3} />)}
            <Bar stackId="a" dataKey="n_facilities" fill="#7eb0eaff" radius={[6, 6, 6, 6]} />
          </ComposedChart>
        </ResponsiveContainer>

      </Grid>
      
    </Stack >
  );
}