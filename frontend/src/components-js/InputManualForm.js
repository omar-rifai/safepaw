
import './forms.css'
import { useState, useEffect, useContext, useMemo } from 'react'
import { FormControl, InputLabel, Select, MenuItem, Box, Button, CircularProgress } from "@mui/material";
import { DynamicSlider } from './SliderForm';
import { DataContext } from '../App';

export default function ManualInputForm() {

    const { inputData, setInputData, setOutputData } = useContext(DataContext);

    const [regions, setRegions] = useState([])
    const [departmentsRegions, setDepartmentsRegions] = useState([])
    const [selectedDepartment, setSelectedDepartment] = useState("")
    const [selectedRegion, setSelectedRegion] = useState("")
    const [error, setError] = useState([])
    const [loading, setLoading] = useState(false)
    const [demand, setDemand] = useState(0)
    const [transfers, setTransfers] = useState(1)
    const [global_capacity, setGlobalCapacity] = useState(0)

    const regionID = "region-label";
    const departmentID = "department-label";

    const filteredDepartments = useMemo(
        () =>
            departmentsRegions
                .filter(d => d.region_name == selectedRegion)
                .map(d => d.dep_name),
        [departmentsRegions, selectedRegion]
    );

    const handleRegionChange = (region) => {
        setSelectedRegion(region)
        setOutputData(null)
        setDemand(0);
        setGlobalCapacity(0);
        setTransfers(1);
    };

    const handleDepartmentChange = (dep) => {
        setSelectedDepartment(dep)
        setOutputData(null)
        setDemand(0);
        setGlobalCapacity(0);
        setTransfers(1);
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true)

        const payloadData = {
            dict_instance: inputData.dict_instance,
            transfers: transfers,
            region: selectedRegion,
            department: selectedDepartment,
        }

        const payload = JSON.stringify(payloadData)

        try {
            const res = await fetch("/api/optimize_maternite", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: payload,
            });

            const data = await res.json();

            if (!res.ok) {
                setError(data.error || "Server error");
                return;
            }

            if (setOutputData) setOutputData(data);
        }

        catch {
            setError("Network error");
        }
        finally {
            setLoading(false)
        }
    };

    useEffect(() => {
        fetch("data/departments-region.json")
            .then(res => res.json())
            .then(data => {
                const unique_regions = [... new Set(data.map(d => d.region_name))];
                setRegions(unique_regions)
                setDepartmentsRegions(data)
            });
    }, []);


    useEffect(() => {
        if (!selectedRegion) return;
        const payload = selectedDepartment
            ? { region: selectedRegion, department: selectedDepartment }
            : { region: selectedRegion };

        fetch("/api/read_maternites", {
            method: "POST",
            body: JSON.stringify(payload),
            headers: { "Content-Type": "application/json" }
        })
            .then(res => res.json())
            .then(data => {
                setInputData(data);
            })
    }, [selectedDepartment, selectedRegion]);


    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, pl: 2 }} >
            <FormControl fullWidth sx={{ maxWidth: 300 }} margin="normal">
                <InputLabel id={regionID}> Regions </InputLabel>
                <Select label="Regions" labelId={regionID} value={selectedRegion} onChange={
                    e => {
                        handleRegionChange(e.target.value);
                        setSelectedDepartment("")
                    }}>

                    {regions.map((region) => (
                        <MenuItem key={region} value={region}>
                            {region}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl fullWidth sx={{ maxWidth: 300 }} margin="normal">
                <InputLabel id={departmentID}> Departements </InputLabel>
                <Select label="Departments" labelId={departmentID} value={selectedDepartment} onChange={
                    e => {
                        handleDepartmentChange(e.target.value);
                    }}>
                    <MenuItem value=""> <em>None</em> </MenuItem>
                    {filteredDepartments.map((dep) => (
                        <MenuItem key={dep} value={dep}>
                            {dep}
                        </MenuItem >
                    ))}
                </Select>
            </FormControl>

            <DynamicSlider label={inputData.demand_total ? `Demand (patients): ${inputData.demand_total}` : `Demand`} value={demand} SetValue={setDemand} dict_key="demand"></DynamicSlider>
            <DynamicSlider label={inputData.capacity_total ? `Capacity (beds): ${inputData.capacity_total}` : `Global capacity`} value={global_capacity} SetValue={setGlobalCapacity} dict_key="global_capacity" ></DynamicSlider>
            <DynamicSlider label={"Max Transfers (%): " + transfers} value={transfers} SetValue={setTransfers} frac={true} dict_key="max_transfers" ></DynamicSlider>

            <Box sx={{ display: 'flex', borderRadius: 2, mt: 3,  mb :4 }}>
                <Button
                    variant="contained"
                    component="label"
                    size="small"
                    onClick={handleSubmit}
                    sx={{ alignSelf: 'flex-start' }}
                >
                    Submit
                </Button>
                {loading && <CircularProgress sx={{ ml: 4 }} /> }
            </Box>
            
        </Box>
    );
}

