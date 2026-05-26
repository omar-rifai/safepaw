
import { DataContext } from '../../App';
import { useContext } from "react";
import GaugeChart from './GaugeForm';
import { Grid } from '@mui/system';



export default function ConfigChart() {
    const { inputData } = useContext(DataContext);
    const instance = inputData?.entries?.instance

    const capacityFrac = instance?.perc_capacity;
    const demandFrac = instance?.perc_demand;
    const alphaFrac = instance?.alpha;
    const transfersFrac = instance?.perc_transfers;
    const total_demand = instance?.total_demand;


    const capacity_label = capacityFrac > 1 ? `+ ${Math.round((capacityFrac - 1) * 100)}%` : capacityFrac < 1 ? `-${Math.round((1 - capacityFrac) * 100)}%` : '+0%'
    const normalized_capacity = (capacityFrac - 0.5);
    const normalized_demand = (demandFrac - 0.5);


    const n_patients = Math.round(total_demand * demandFrac)

    const steps = 21;
    const positive_gradients = ['#ca8380ff', '#f2f0daff', '#99c575ff'];
    const negative_gradients = ['#99c575ff', '#f2f0daff', '#ca8380ff'];
    const uniform_stops = ['#ced6e9ff', '#3b4868ff'];

    const activeIndexCapacity = Math.round(normalized_capacity * (steps - 1));
    const activeIndexDemand = Math.round(normalized_demand * (steps - 1));
    const activeIndexAlpha = Math.round(alphaFrac * (steps - 1));
    const activeIndexTransfers = Math.round(transfersFrac * (steps - 1));

    return (
        <Grid container spacing={5} sx={{ justifyContent: "space-evenly", alignItems: "flex-start", mt: 15 }}>
            <Grid >
                <GaugeChart activeIndex={activeIndexCapacity} steps={steps} stops={positive_gradients} label={`Global Capacity: ${capacity_label}`} />
            </Grid>
            <Grid  >
                <GaugeChart activeIndex={activeIndexDemand} steps={steps} stops={negative_gradients} label={`Number of Patients: ${n_patients}`} />
            </Grid>
            <Grid >
                <GaugeChart activeIndex={activeIndexAlpha} steps={steps} stops={uniform_stops} label={`Alpha (α): ${alphaFrac}`} />
            </Grid>
            <Grid >
                <GaugeChart activeIndex={activeIndexTransfers} steps={steps} stops={uniform_stops} label={`Resources Transfers: ${transfersFrac}`} />
            </Grid>
        </Grid>
    );
}