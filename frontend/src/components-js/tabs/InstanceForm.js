

import { Card, Slider, Grid, Stack, Typography } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../../App';
import { useState } from 'react';

export default function InstancesForm() {
    const { inputData } = useContext(DataContext);
    const [alphaValue, setAlphaValue] = useState(inputData.instance?.alpha ? inputData.instance.alpha : 0)
    const handleChange = (event, newValue) => {
        setAlphaValue(newValue);
    };
    return (
        < Card>
            <Stack sx={{ m: 10, display: "flex", gap: 3 }}>
                <Grid sx={{ display: "flex", gap: 3 }}>
                    <Grid size={4}>
                        <Typography fontWeight={500} fontSize="0.95rem">Global demand</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Slider aria-label='Test' value={inputData.instance?.alpha} min={0} max={1} step={0.01} onChange={handleChange} />
                    </Grid>
                </Grid>
                <Grid sx={{ display: "flex", gap: 3 }}>
                    <Grid size={4}>
                        <Typography  fontWeight={500} fontSize="0.95rem">Global capacity:</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Slider aria-label='Test' value={inputData.instance?.alpha} min={0} max={1} step={0.01} onChange={handleChange} />
                    </Grid>
                </Grid>
                <Grid sx={{ display: "flex", gap: 3 }}>
                    <Grid size={4}>
                        <Typography fontWeight={500} fontSize="0.95rem">Max transfers (%)</Typography>
                    </Grid>
                    <Grid size={8}>
                        <Slider aria-label='Test' value={inputData.instance?.alpha} min={0} max={1} step={0.01} onChange={handleChange} />
                    </Grid>
                </Grid>
            </Stack>
        </Card >
    );
}