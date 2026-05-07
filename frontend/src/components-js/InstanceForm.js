

import { Card, Slider, Box, Typography } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../App';
import { useState } from 'react';

export default function InstancesForm() {
    const { inputData } = useContext(DataContext);
    const [alphaValue, setAlphaValue] = useState(inputData.instance?.alpha ? inputData.instance.alpha : 0)
    const handleChange = (event, newValue) => {
        setAlphaValue(newValue);
    };
    return (
        < Card>
            <Box sx={{ m: 10 }}>
                <Typography>Test</Typography>
                <Slider aria-label='Test' value={inputData.instance?.alpha} min={0} max={1} step={0.01} onChange={handleChange} />
            </Box>
        </Card >
    );
}