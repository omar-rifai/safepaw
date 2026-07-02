import { Box, Button, Select, InputLabel, MenuItem, FormControl } from "@mui/material"
import departments from "../departments.json"
import { styled } from '@mui/material/styles';
import { DataContext } from "../App";
import { UIContext } from "../App";
import { useContext, useEffect, useState } from "react";
import Snackbar from '@mui/material/Snackbar';

export default function ToolbarForm() {
    const [isGenerating, setIsGenerating] = useState(false)
    const [depCode, setDepCode] = useState("")
    const [datasetType, setDatasetType] = useState("")
    const [openSnackBar, setOpenSnackBar] = useState(false)


    const { openJobsPanel, setOpenJobsPanel } = useContext(UIContext)
    const { setOutputData, setInputData, inputData, setActiveTab, isOptimizing, setIsOptimizing } = useContext(DataContext);

    const departments_maternities = [
        "06", "10", "13", "14", "21", "22", "25", "29", "30", "31", "33", "34",
        "35", "37", "38", "42", "44", "45", "49", "50", "51", "54", "56", "59",
        "60", "62", "63", "64", "66", "67", "68", "69", "72", "73", "75", "76",
        "77", "78", "80", "86", "87", "91", "92", "93", "94", "95"
    ]

    const departments_pthptg = [
        "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "21", "22",
        "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34",
        "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46",
        "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58",
        "59", "60", "61", "62", "63", "64", "65", "66", "68", "69", "70", "71",
        "72", "73", "74", "76", "77", "78", "79", "80", "81", "82", "83", "84",
        "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95"]

    useEffect(() => {
        setDatasetType(inputData.entries?.instance?.id ?? "")
        setDepCode(inputData.entries?.instance?.dep_code ?? "")
    }, [inputData])

    function handleCloseSnackBar(){
        setOpenSnackBar(false)
    }

    function changeDatasetType(dataset_type) {
        setDepCode("")
        setDatasetType(dataset_type)
    }

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

    function generateInstance(dep_code) {

        const callGenerateAPI = async () => {
            console.log("Generating new instance:", datasetType, dep_code)
            const old_code = depCode
            setDepCode(dep_code)
            setIsGenerating(true)

            const response = await fetch("/api/generate", {
                method: "POST",
                body: JSON.stringify({ "mode": datasetType, "dep_code": dep_code }),
                headers: { "Content-Type": "application/json" }
            })

            if (!response.ok) {
                const error = await response.json()
                alert(error.detail);
                setIsGenerating(false)
                setDepCode(old_code)
                return
            }

            const payload = await response.json()
            setInputData(payload)
            setOutputData(null)
            setActiveTab("tab-facilities")
            setIsGenerating(false)
        };
        callGenerateAPI()
    }

    const disabled_generate = (!datasetType) || isGenerating
    const disabled_optimize = !datasetType || !depCode || isGenerating
    const disabled_selection = isGenerating
    const filtered_departments = datasetType === "maternities" ? departments.filter((e) => departments_maternities.includes(e.code)) :
        datasetType == "pthptg" ? departments.filter((e) => departments_pthptg.includes(e.code)) : [];

    const optimizeInstance = async () => {
        console.log("Calling optimize_instance..")
        setIsOptimizing(true)

        const submit_response = await fetch("/api/submit_job", {
            method: "POST",
            body: JSON.stringify({ "instance": inputData?.entries?.instance, "mode": datasetType, "dep_code": depCode }),
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
        setOpenSnackBar(true)
        setIsOptimizing(false)

        async function loadState() {
            const res = await fetch("/api/get_state");
            const data = await res.json()
            setInputData(data)
        }
        loadState()
    };


    return (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, m: 1, minWidth: 900 }}>
            <Button size="small" component="label" sx={{ flexShrink: 0 }}>  Upload File <VisuallyHiddenInput type="file" onChange={handleUpload} multiple /></Button>
            <FormControl sx={{ m: 1, minWidth: 180 }}>
                <InputLabel size="small" >Dataset Type</InputLabel>
                <Select disabled={disabled_selection} value={datasetType ?? ""} size="small" label="dataset type" sx={{ width: 190 }} onChange={(e) => { changeDatasetType(e.target.value) }}>
                    <MenuItem key={""} value={""}>  </MenuItem>
                    <MenuItem key={"maternities"} value={"maternities"}> French Maternities </MenuItem>
                    <MenuItem key={"pthptg"} value={"pthptg"}> Hip/Knee Prosthesis </MenuItem>
                </Select>
            </FormControl>
            <FormControl sx={{ m: 1, minWidth: 120 }}>
                <InputLabel size="small" >Department</InputLabel>
                <Select disabled={disabled_generate} value={depCode ?? ""} label="department" size="small" sx={{ width: 190 }}>
                    <MenuItem value={""}>  </MenuItem>
                    {filtered_departments.map((department) => (
                        <MenuItem key={department.code} value={department.code}  onClick={(e) => (generateInstance(department.code))}>{department.dep_name}</MenuItem>)
                    )}

                </Select>
            </FormControl>
            <Box sx={{ width: 15 }} />
            {false && <Button size="small" disabled={disabled_generate} loading={isGenerating} variant="contained" onClick={generateInstance} sx={{ flexShrink: 0 }} >Generate</Button>}
            <Button size="small" loading={isGenerating || isOptimizing} variant="contained" onClick={optimizeInstance} sx={{ flexShrink: 0 }} disabled={disabled_optimize}>Optimize</Button>
            <Button size="small" color="secondary" variant="contained" onClick={() => { setOpenJobsPanel(!openJobsPanel) }} sx={{ flexShrink: 0 }}>Jobs Panel</Button>
            <Snackbar open={openSnackBar} autoHideDuration={2000} message="Job Submitted" onClose={handleCloseSnackBar}/>
        </Box>

    )
}