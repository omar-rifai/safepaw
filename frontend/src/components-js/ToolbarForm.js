import { Box, Button, Select, InputLabel, MenuItem, FormControl } from "@mui/material"
import departments from "../departments.json"
import { styled } from '@mui/material/styles';
import { DataContext } from "../App";
import { UIContext } from "../App";
import { useContext, useEffect, useState } from "react";

export default function ToolbarForm() {
    const [isGenerating, setIsGenerating] = useState(false)
    const [isOptimizing, setIsOptimizing] = useState(false)
    const [depCode, setDepCode] = useState("")
    const [datasetType, setDatasetType] = useState("")

    const { openJobsPanel, setOpenJobsPanel } = useContext(UIContext)
    const { setOutputData, setInputData, inputData, setActiveTab } = useContext(DataContext);


    useEffect(() => {
        setDatasetType(inputData.instance_data?.instance_mode ?? "")
        setDepCode(inputData.instance_data?.dep_code ?? "")
    }, [inputData])



    const VisuallyHiddenInput = styled('input')({
        clip: 'rect(0 0 0 0)', clipPath: 'inset(50%)', height: 1, overflow: 'hidden', position: 'absolute', bottom: 0, left: 0,
        whiteSpace: 'nowrap', width: 1,
    });


    const handleUpload = async (event) => {
        console.log("in handleUpload function")
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
        setIsGenerating(true)

        const response = await fetch("/api/generate", {
            method: "POST",
            body: JSON.stringify({ "mode": datasetType, "dep_code": depCode }),
            headers: { "Content-Type": "application/json" }
        })

        if (!response.ok) {
            const error = await response.json()
            alert(error.detail);
            setIsGenerating(false)
            return
        }

        const payload = await response.json()
        setInputData(payload)
        setOutputData(null)
        setActiveTab("tab-facilities")
        setIsGenerating(false)
    };


    const enabled_optimize = inputData?.entries ? false : true

    const disabled_generate = (depCode == "") || (datasetType == "")

    const optimizeInstance = async () => {
        console.log("Calling optimize_instance..")
        setIsOptimizing(true)

        const submit_response = await fetch("/api/submit_job", {
            method: "POST",
            body: JSON.stringify({ "instance": inputData?.entries?.instance }),
            headers: { "Content-Type": "application/json" }
        })

        if (!submit_response.ok) {
            const error = await submit_response.json()
            alert(error.detail);
            setIsOptimizing(false)
            return
        }

        const payload_submit = await submit_response.json()
        const job_id = payload_submit["job_id"]
        console.log("job id:", job_id)

        const retrieve_response = await fetch(`/api/retrieve_job/${job_id}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        })

        if (!retrieve_response.ok) {
            const error = await retrieve_response.json()
            alert(error.detail);
            setIsOptimizing(false)
            return
        }

        const payload_retrieve = await retrieve_response.json()
        if (payload_retrieve["status"] == "Infeasible") {
            alert("Could not optimize instance. Please modify instance parameters and try again.")
            setIsOptimizing(false)
            return
        }

        setOutputData(payload_retrieve)
        setIsOptimizing(false)
        setActiveTab("tab-resources")

        async function loadState() {
            const res = await fetch("/api/get_state");
            const data = await res.json()
            setInputData(data)}
        loadState()
    };


    return (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, m: 1, minWidth: 900 }}>
            <Button size="small" component="label" sx={{ flexShrink: 0 }}>  Upload File <VisuallyHiddenInput type="file" onChange={handleUpload} multiple /></Button>
            <FormControl sx={{ m: 1, minWidth: 180 }}>
                <InputLabel size="small" >Dataset Type</InputLabel>
                <Select value={datasetType} size="small" label="dataset type" sx={{ width: 190 }} onChange={(e) => (setDatasetType(e.target.value))}>
                    <MenuItem key={""} value={""}>  </MenuItem>
                    <MenuItem key={"maternities"} value={"maternities"}> French Maternities </MenuItem>
                    <MenuItem key={"pthptg"} value={"pthptg"}> Hip/Knee Prosthesis </MenuItem>
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 120 }}>
                <InputLabel size="small" >Department</InputLabel>
                <Select value={depCode} label="department" size="small" sx={{ width: 190 }} onChange={(e) => (setDepCode(e.target.value))}>
                    <MenuItem value={""}>  </MenuItem>
                    {departments.map((e) => (
                        <MenuItem key={e.code} value={e.code}>{e.dep_name}</MenuItem>)
                    )}

                </Select>
            </FormControl>
            <Box sx={{ width: 15 }} />
            <Button size="small" disabled={disabled_generate} loading={isGenerating} variant="contained" onClick={generateInstance} sx={{ flexShrink: 0 }} >Generate</Button>
            <Button size="small" loading={isOptimizing} variant="contained" onClick={optimizeInstance} sx={{ flexShrink: 0 }} disabled={enabled_optimize}>Submit Job</Button>
            <Button size="small" color="secondary" variant="contained" onClick={() => { setOpenJobsPanel(!openJobsPanel) }} sx={{ flexShrink: 0 }} disabled={enabled_optimize}>Jobs Panel</Button>


        </Box>
    )
}