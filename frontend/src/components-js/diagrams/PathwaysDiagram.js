import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, ReferenceLine } from "recharts";
import { Card, Box, Typography,  Grid } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext} from "react";


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
        <Grid sx={{ width: 800 }}>
            <Card sx={{ width: "100%", mx: "auto", mt: 10 }}>
                <Typography sx={{pl:"10%", fontFamily: "Roboto" }}> Number of Healthcare Facilities with Pathway</Typography>
                <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>

                    <ResponsiveContainer width="100%" height={400} style={{ flex: 1, minWidth: 0 }}>
                        <ComposedChart data={chartData}
                            margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>

                            <Tooltip />

                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="pathway_id" padding={{ left: 30, right: 30 }} label='Pathway ID' />
                            <YAxis width="auto" label={{ value: 'Number of facilities', angle: -90 }} />
                            <Legend />
                            <ReferenceArea x1={selectedPathways[0]} x2={selectedPathways[selectedPathways.length - 1]}
                                fill="#88adc8ff" fillOpacity={0.3} />
                            <Bar stackId="a" dataKey="n_facilities" fill="#88adc8ff" />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Box>
            </Card>
        </Grid>

    );
}