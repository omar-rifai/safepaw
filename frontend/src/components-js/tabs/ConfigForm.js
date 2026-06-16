
import { Box, Button, Stack, Typography, Slider, Divider } from "@mui/material";
import { useContext } from "react";
import { DataContext } from "../../App";


export default function ConfigForm() {

    const { inputData, setInputData, setOutputData } = useContext(DataContext)

    const handleClearOutput  = function(){
        setOutputData({})
    }

    const handleReset  = function(){
        setOutputData({})
        setInputData({})
    }
    return (
        <Box sx={{ flexGrow: 1, minWidth: 0, width: "100%", ml: 2 }}>

            <Stack container spacing={2} sx={{ mt: 3, mr: 10, mb: 5 }} >
                <Stack container direction="row" alignItems="center" >
                    <Typography sx={{ pl: "5%", mt: 4, fontSize: 24 }}>Settings</Typography>
                </Stack>
                <Divider />
                <Stack container direction="row" alignItems="center" >
                    <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Capacity variation (%)</Typography>
                    <DynamicSlider
                        value={inputData?.entries?.instance?.perc_capacity ?? 0} param_key="perc_capacity">
                    </DynamicSlider>
                </Stack>
                <Stack container direction="row" alignItems="center" >
                    <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Demand variation (%)</Typography>
                    <DynamicSlider
                        value={inputData?.entries?.instance?.perc_demand ?? 0} param_key="perc_demand">
                    </DynamicSlider>
                </Stack>

                <Stack container direction="row" alignItems="center" >
                    <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Allowed tranfers (%)</Typography>
                    <DynamicSlider
                        value={inputData?.entries?.instance?.perc_transfers ?? 0} frac={true} param_key="perc_transfers">
                    </DynamicSlider>
                </Stack>
                                <Stack container direction="row" alignItems="center" >
                    <Typography sx={{ ml: 5, width: 180, fontSize: 15 }}>Alpha </Typography>
                    <DynamicSlider
                        value={inputData?.entries?.instance?.alpha ?? 0} frac={true} param_key="alpha">
                    </DynamicSlider>
                </Stack>
                <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, mt: 2 }}>
                    <Button onClick={handleClearOutput}>Clear Output</Button>
                    <Button onClick={handleReset}>Reset</Button>
                </Box>

            </Stack>

        </Box >
    );
}


function DynamicSlider({ value, frac = false, param_key }) {

    const { setInputData } = useContext(DataContext);

    const min = frac ? 0 : -50
    const max = frac ? 1 : 50
    const step = frac ? 0.1 : 5;

    const handleChange = async (_, newVal) => {

        const api_value = frac ? newVal : 1 + (newVal / 100);
        setInputData(prev => ({
            ...prev,
            entries: {
                ...(prev?.entries ?? {}),
                instance: {
                    ...(prev?.entries?.instance ?? {}),
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
