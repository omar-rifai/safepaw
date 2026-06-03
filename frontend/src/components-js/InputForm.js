import { Grid, Box, Button, Typography, Select } from "@mui/material"
import { styled } from '@mui/material/styles';
import { DataContext  } from "../App";
import { useContext } from "react";

export default function InputForm() {

    const {setOutputData,setInputData, inputData, setActiveTab} = useContext(DataContext);

    const VisuallyHiddenInput = styled('input')({
        clip: 'rect(0 0 0 0)', clipPath: 'inset(50%)', height: 1, overflow: 'hidden', position: 'absolute', bottom: 0, left: 0,
        whiteSpace: 'nowrap', width: 1,
    });

    const handleUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const text = await file.text();
        const jsonData = JSON.parse(text)

        const response = await fetch("/api/read_file", {
            method: "POST",
            body: JSON.stringify(jsonData),
            headers: { "Content-Type": "application/json" }

        })
        const result = await response.json();
        setInputData(prev => ({
            ...prev,
            ...result
        }));
        setOutputData(null)
        setActiveTab("tab-facilities")
    };


    const enabled_optimize = inputData?.entries ? false : true
    const optimizeInstance = async () => {
        console.log("Calling optimize_instance..")

        const response_convert = await fetch("/api/optimize", {
            method: "POST",
            body: JSON.stringify({ "instance": inputData?.entries?.instance }),
            headers: { "Content-Type": "application/json" }
        })

        const payload = await response_convert.json()
        setOutputData(payload)
        setActiveTab("tab-resources")
    };

    return (
        <Grid sx={{ display: "flex", alignItems: "center", gap: 1, m:1, minWidth:700}}>
            <Typography>Dataset:</Typography>
            <Select size="small" sx={{ width: 150 }}></Select>

            <Typography>Department:</Typography>
            <Select size="small" sx={{ width: 150 }}></Select>
            <Box sx={{ width: 15 }} />
            <Button size="small" variant="contained" onClick={optimizeInstance} sx={{ flexShrink: 0 }} disabled={enabled_optimize}>Generate</Button>
            <Button size="small" variant="contained" onClick={optimizeInstance} sx={{ flexShrink: 0 }} disabled={enabled_optimize}>Optimize</Button>
            <Button size="small" component="label" sx={{ flexShrink: 0 }}>  Upload <VisuallyHiddenInput type="file" onChange={handleUpload} multiple /></Button>
            
        </Grid>
    )
}