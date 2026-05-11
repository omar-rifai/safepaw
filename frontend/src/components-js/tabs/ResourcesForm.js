

import { Card, Select, Grid, Stack, Typography, MenuItem, Chip, FormControlLabel, Radio} from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../../App';
import { useState } from 'react';

export default function InstancesForm() {
    const { inputData } = useContext(DataContext);

    return (
        < Card >
            <Stack sx={{ m: 3, gap: 3 }} >


                <Grid sx={{ display: "flex", gap: 3 }}>
                    <Typography> Facility</Typography>
                    <Select sx={{ width: 300 }}>
                        {inputData.instance?.facilities.map((h) => (
                            <MenuItem key={h["facility_id"]} value={h["facility_id"]}>
                                {h["facility_name"]}
                            </MenuItem >
                        ))}

                    </Select>
                </Grid>
                <Chip
                    label={
                        <FormControlLabel
                            control={<Radio/>}
                            label="Option A"
                        />
                    }
                />
            </Stack>
        </Card >
    );
}