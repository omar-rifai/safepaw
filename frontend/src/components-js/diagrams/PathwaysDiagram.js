import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, ReferenceLine } from "recharts";
import { Card, Box, Typography, Grid } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext } from "react";


export default function PathwaysChart() {

    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);

    const pathways = inputData?.entries?.pathways ? inputData.entries.pathways :
        null

    const pathways_unique = pathways.filter((obj1, i, arr) =>
        arr.findIndex(obj2 => ['facility_id', 'pathway_id'].every(key => obj2[key] === obj1[key])
        ) === i
    )

    const chartData = Object.values(
        pathways_unique.reduce((acc, { pathway_id }) => {
            acc[pathway_id] ??= { pathway_id, n_facilities: 0 };
            acc[pathway_id].n_facilities++;
            return acc;
        }, {})
    );
    const selectedPathways = pathways_unique
        .filter((e) => e.facility_id === selectedFacilityID)
        .map((e) => e.pathway_id);


    return (
        <Grid container sx={{ width: 300, height: 300 }}>

            <Typography sx={{ pl: "10%" }}> Healthcare Facilities Count (per pathway type)</Typography>


            <ResponsiveContainer width="100%" height="100%" style={{ flex: 1, minWidth: 0, background: "#fff", borderRadius: 2, p: 1  }}>
                <ComposedChart data={chartData} barCategoryGap="20%" layout="vertical" margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>

                    <Tooltip />

                    <CartesianGrid  strokeDasharray="3 3" strokeOpacity={0.5} />
                    <XAxis type="number" />
                    <YAxis dataKey="pathway_id" label={{ value: "Pathway ID", angle: -90, position: "insideLeft" }} type="category" />
                    <Legend />
                    <ReferenceArea y1={selectedPathways[0]} y2={selectedPathways[selectedPathways.length - 1]}
                        fill="#88adc8ff" fillOpacity={0.3} />
                    <Bar stackId="a" dataKey="n_facilities" fill="#7eb0eaff" radius={[6, 6, 6, 6]} />
                </ComposedChart>
            </ResponsiveContainer>

        </Grid>

    );
}