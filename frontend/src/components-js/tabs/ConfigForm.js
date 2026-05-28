
import { Card, Grid, Stack, Typography, Slider, Divider } from "@mui/material";
import { useContext } from "react";
import { DataContext } from "../../App";


export default function ConfigForm() {

    const { inputData } = useContext(DataContext)

    return (
        <Grid >
            <Card sx={{ width: 550, height: "auto", }}>
                <Stack container spacing={2} sx={{ mt: 3, ml: 3, mr: 10, mb: 5 }} >
                    <Stack container direction="row" alignItems="center" >
                        <Typography sx={{ pl: "5%", mt: 4, fontSize: 15 }}>Settings</Typography>
                    </Stack>
                    <Divider />
                    <Stack container direction="row" alignItems="center" >
                        <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Global capacity (%)</Typography>
                        <DynamicSlider
                            value={inputData?.entries?.instance?.perc_capacity ?? 0}  param_key="perc_capacity">
                        </DynamicSlider>
                    </Stack>
                    <Stack container direction="row" alignItems="center" >
                        <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Demand (%)</Typography>
                        <DynamicSlider
                            value={inputData?.entries?.instance?.perc_demand ?? 0} param_key="perc_demand">
                        </DynamicSlider>
                    </Stack>
                    <Stack container direction="row" alignItems="center" >
                        <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Alpha </Typography>
                        <DynamicSlider
                            value={inputData?.entries?.instance?.alpha ?? 0} frac={true} param_key="alpha">
                        </DynamicSlider>
                    </Stack>
                    <Stack container direction="row" alignItems="center" >
                        <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Allowed tranfers (%)</Typography>
                        <DynamicSlider
                            value={inputData?.entries?.instance?.perc_transfers ?? 0} frac={true}  param_key="perc_transfers">
                        </DynamicSlider>
                    </Stack>

                </Stack>
            </Card>
        </Grid >
    );
}


function DynamicSlider({ value, frac = false, param_key }) {

    const { setInputData } = useContext(DataContext);

    const min = frac ? 0 : -50
    const max = frac ? 1 : 50
    const step = frac ? 0.1 : 5;

    const handleChange = async (event, newVal) => {
       
        const api_value = frac ? newVal : 1 + (newVal / 100);
        setInputData(prev=>({
            ...prev,
            entries: {
                ...(prev?.entries??{}),
                instance: {
                    ...(prev?.entries?.instance?? {}),
                    [param_key]: api_value
                }
            }
        }));
    };

    return (
        <Slider track={false}
            step={step}
            sx={{ flex: 1 }}
            marks
            min={min} max={max}
            value={frac ? value : ((value ?? 1) - 1) * 100}
            valueLabelDisplay="auto"
            valueLabelFormat={(v) => frac ? v : `${v > 0 ? "+" : ""}${Number(v.toFixed(2))} %`}
            onChange={handleChange}>
        </Slider>

    )
}
