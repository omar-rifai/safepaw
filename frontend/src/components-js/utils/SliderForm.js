import { Stack, FormLabel, Slider } from '@mui/material';
import {useState} from "react"

export function SliderForm({ label, value }) {

    const [cursorValue, setCursorValue] = useState(value)

    const handleChange = async (event, newVal) => {
        setCursorValue(newVal);
    }

    return (
        <Stack spacing={2} direction="row" sx={{ alignItems: 'center', mb: 1 }}>
            <FormLabel >{label}</FormLabel>
            <Slider track={false}
                color={"primary"}
                step={0.1}
                marks
                min={0} max={1}
                value={value}
                valueLabelDisplay="auto"
                valueLabelFormat={(v) =>  `${v} %`}
                onChange={handleChange}
            ></Slider>
        </Stack>
    )
}