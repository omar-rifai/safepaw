import { Grid, Card, CardContent, Typography } from "@mui/material";
import './forms.css';
import { useContext } from "react";
import { DataContext } from "../App";

function DashboardForm() {

    const { inputData } = useContext(DataContext);

    if (!inputData?.dashboard_stats) {

        return <Typography>Upload stats to see dashboard summary.</Typography>;
    }

    const formatLabel = (key) => key.replace(/_/g, ' ');

    return (
        <Grid container spacing={2}>
            {Object.entries(inputData.dashboard_stats).map(([key, value]) => (
                <Grid item xs={12} sm={6} md={4} key={key}>
                    <Card elevation={3}>
                        <CardContent>
                            <Typography color="textSecondary" variant="subtitle2">
                                {formatLabel(key)}
                            </Typography>
                            <Typography variant="h10" fontWeight="bold">
                                {value}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            )
            )}

        </Grid>
    );
}

export default DashboardForm;
