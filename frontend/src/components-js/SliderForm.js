import { FormControl, FormLabel, Slider } from '@mui/material';
import { Typography, Box, Stack } from '@mui/material';
import { useEffect } from 'react'
import { useContext } from "react";
import { DataContext } from "../App";


export function DynamicSlider({ label, value, SetValue, frac = false, dict_key}) {

    const { inputData, setInputData } = useContext(DataContext);

    const min = frac ? 0 : -50
    const max = frac ? 1 : 50
    const step = frac ? 0.1 : 10;

    const handleChange =  async (event, newVal) => {
        SetValue(newVal);

        try {
            const response = await fetch("api/update_maternites",
                {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ...inputData, [dict_key]: newVal })
                }
            );

            if (!response.ok) throw new Error("Network response error while update Inputs");
            const updatedData = await response.json()

            setInputData(updatedData);
        }
        catch(err) {
            console.error("Failed to update inputData.", err)
        }
    };

    useEffect(() => {
        frac? SetValue(1): SetValue(0);
    }, [inputData.department]);

    return (
        <FormControl sx={{ maxWidth: 300 }}>
            <FormLabel >{label}</FormLabel>
            <Slider track={false}
                color={frac ? "secondary" : "primary"}
                step={step}
                marks
                min={min} max={max}
                value={value} 
                valueLabelDisplay="auto"
                valueLabelFormat={(v) => frac? v : `${v > 0 ? "+" : ""}${v} %`}
                onChange={handleChange}
            ></Slider>
        </FormControl>
    )
}


export function LegacySlider({ text_label, min_val, max_val, step, curr_val, onChange }) {
    return (
        <Box mb={2} sx={{ width: '100%' }}>
            <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
                <Typography sx={{ minWidth: 250, flex: '0 1 auto', textAlign: 'left' }} variant="body1">
                    {text_label} : {curr_val}
                </Typography>

                <input
                    id="slider"
                    type="range"
                    min={min_val}
                    max={max_val}
                    step={step}
                    value={curr_val}
                    onChange={(e) => onChange(parseFloat(e.target.value))}
                    style={{ flexGrow: 1, maxWidth: '200px' }} // slider takes remaining space
                />
            </Stack >
        </Box>

    )
} 