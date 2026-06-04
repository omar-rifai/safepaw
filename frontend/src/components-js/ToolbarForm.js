import { Grid, Box, Button, Select, InputLabel, MenuItem, FormControl } from "@mui/material"
import departments from "../departments.json"
import { styled } from '@mui/material/styles';
import { DataContext } from "../App";
import { useContext, useEffect, useState } from "react";

export default function ToolbarForm() {

    const [depCode, setDepCode] = useState("")
    const [datasetType, setDatasetType] = useState("")

    const { setOutputData, setInputData, inputData, setActiveTab } = useContext(DataContext);


    useEffect(()=>{
        setDatasetType(inputData.instance_data?.instance_mode ?? "")
        setDepCode(inputData.instance_data?.dep_code ?? "")
    },[inputData])

    
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


    const generateInstance = async () => {
        console.log("Generating new instance:", datasetType, depCode)

        const response_convert = await fetch("/api/generate", {
            method: "POST",
            body: JSON.stringify({ "mode": datasetType, "dep_code": depCode }),
            headers: { "Content-Type": "application/json" }
        })

        const payload = await response_convert.json()
        setInputData(payload)
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
        <Grid sx={{ display: "flex", alignItems: "center", gap: 1, m: 1, minWidth: 700 }}>

            <FormControl sx={{ m: 1, minWidth: 120 }}>
                <InputLabel size="small" >Dataset Type</InputLabel>
                <Select value={datasetType} size="small" label="dataset type" sx={{ width: 150 }} onChange={(e)=>(setDatasetType(e.target.value))}>
                    <MenuItem key={""} value={""}>  </MenuItem>
                    <MenuItem key={"maternities"} value={"maternities"}> French Maternities </MenuItem>
                    <MenuItem key={"pthptg"} value={"pthptg"}> Hip/Knee Prosthesis </MenuItem>
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 120 }}>
                <InputLabel size="small" >Department</InputLabel>
                <Select value={depCode} label="department" size="small" sx={{ width: 190 }} onChange={(e)=>(setDepCode(e.target.value))}>
                    <MenuItem value={""}>  </MenuItem>
                    {departments.map((e) => (
                        <MenuItem key={e.code} value={e.code}>{e.dep_name}</MenuItem>)
                    )}

                </Select>
            </FormControl>
            <Box sx={{ width: 15 }} />
            <Button size="small" variant="contained" onClick={generateInstance} sx={{ flexShrink: 0 }} >Generate</Button>
            <Button size="small" variant="contained" onClick={optimizeInstance} sx={{ flexShrink: 0 }} disabled={enabled_optimize}>Optimize</Button>
            <Button size="small" component="label" sx={{ flexShrink: 0 }}>  Upload <VisuallyHiddenInput type="file" onChange={handleUpload} multiple /></Button>

        </Grid>
    )
}