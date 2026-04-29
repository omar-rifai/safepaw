import { FormControl, FormLabel, Slider } from '@mui/material';
import { Typography, Box, Stack } from '@mui/material';
import { useEffect } from 'react'
import { useContext } from "react";
import { DataContext } from "../App";


export function DynamicSlider({ label, value, SetValue, radioValue, jsonFileData, frac = false, dict_key }) {

    const { inputData, setInputData } = useContext(DataContext);

    const min = frac ? 0 : -50
    const max = frac ? 1 : 50
    const step = frac ? 0.1 : 10;

    const handleChange = async (event, newVal) => {
        SetValue(newVal);

        try {
            const json_body = (radioValue == "file" ? jsonFileData : { ...inputData, [dict_key]: newVal, "radioValue": radioValue })
            console.log("json body", json_body)
            const response = await fetch("api/update_maternites",
                {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(json_body)
                }
            );

            if (!response.ok) throw new Error("Network response error while update Inputs");
            const updatedData = await response.json()

            setInputData(updatedData);
        }
        catch (err) {
            console.error("Failed to update inputData.", err)
        }
    };

    useEffect(() => {
        frac ? SetValue(0) : SetValue(0);
    }, [inputData.department]);

    return (
        <FormControl sx={{ maxWidth: 300 }}>
            <FormLabel >{label}</FormLabel>
            <Slider track={false}
                color={frac ? "secondary" : "primary"}
                step={step}
                marks
                disabled = {radioValue == "file" ? true : false}
                min={min} max={max}
                value={value}
                valueLabelDisplay="auto"
                valueLabelFormat={(v) => frac ? v : `${v > 0 ? "+" : ""}${v} %`}
                onChange={handleChange}
            ></Slider>
        </FormControl>
    )
}