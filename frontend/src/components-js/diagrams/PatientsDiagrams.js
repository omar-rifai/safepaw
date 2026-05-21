import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, ReferenceLine } from "recharts";
import { Card, Box, Typography,  Grid } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext} from "react";


export default function PatientsChart() {

    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);

    const groups = inputData?.entries?.patients_groups ?  inputData?.entries?.patients_groups  :
        null


    const chartData = Object.values(
        groups.reduce((acc, { group_id }) => {
            acc[group_id] ??= { group_id, n_facilities: 0 };
            acc[group_id].n_facilities++;
            return acc;
        }, {})
    );

    console.log("groups", chartData)
    const selectedGroups = groups
        .filter((e) => e.facility_id === selectedFacilityID)
        .map((e) => e.group_id);


    return (
        <Grid sx={{ width: 800 }}>
            <Card sx={{ width: "100%", mx: "auto", mt: 10 }}>
                <Typography sx={{pl:"10%", fontFamily: "Roboto" }}> Number of Healthcare Facilities Serving Group</Typography>
                <Box sx={{ display: "flex", flexDirection: "row", width: "100%" }}>

                    <ResponsiveContainer width="100%" height={400} style={{ flex: 1, minWidth: 0 }}>
                        <ComposedChart data={chartData}
                            margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>

                            <Tooltip />

                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="group_id" padding={{ left: 30, right: 30 }} label={{ position: 'insideBottomRight', value: 'Patients Group ID', offset: -10 }}/>
                            <YAxis width="auto" label={{ value: 'Number of facilities', angle: -90 }} />
                            <Legend />
                            <ReferenceArea x1={selectedGroups[0]} x2={selectedGroups[selectedGroups.length - 1]}
                                fill="#88adc8ff" fillOpacity={0.3} />
                            <Bar stackId="a" dataKey="n_facilities" fill="#88adc8ff" />
                        </ComposedChart>
                    </ResponsiveContainer>
                </Box>
            </Card>
        </Grid>

    );
}