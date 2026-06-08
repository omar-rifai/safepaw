import { Box, Button, Dialog, IconButton, DialogTitle, Typography, Paper, Grid, TextField, Select, MenuItem } from "@mui/material"
import { useContext, useState, useEffect } from 'react';
import { UIContext, DataContext } from '../../App';
import DeleteIcon from "@mui/icons-material/Delete";

export default function FacilityDialog({ openDialog, setOpenDialog }) {

    const { inputData, setInputData } = useContext(DataContext)
    const { isPickingLocation, setIsPickingLocation, pickedLocation, setPickedLocation } = useContext(UIContext);
    const [newFacilityName, setNewFacilityName] = useState("")
    const [newFacilityID, setNewFacilityID] = useState(null)
    const [newFacilityRegion, setNewFacilityRegion] = useState(null)
    const [selectedResourceID, setSelectedResourceId] = useState(null)
    const [resourcesIDs, setResourcesIDs] = useState([]);
    const [fetchingRegion, setFetchingRegion] = useState(false)
    const [newResources, setNewResources] = useState([]);
    const [submitted, setSubmitted] = useState(false);

    const handleAddResource = () => {
        if (!newResources.map(e => e.resource_id).includes(selectedResourceID)) {
            setNewResources([...newResources, { resource_id: selectedResourceID, capacity: 0, max_transferable_in: 0, max_transferable_out: 0 }])
        }
    }

    const handleClose = () => {
        setOpenDialog(false);
    };

    const handleCancel = () => {
        setOpenDialog(false);
        setPickedLocation(null)
    };

    useEffect(() => {
        const unique_resources = [...new Set(inputData.entries?.resources.map((e) => e.resource_id))].filter(e => newResources.map(e => e.resource_id).includes(e) == false) ?? []
        setResourcesIDs(unique_resources)
    }, [inputData, newResources])

    const facility_id = newFacilityID ?? "";
    const hasErrorID = submitted && (!/^\d{9}$/.test(facility_id));

    async function getRegionID(lat, lon) {
        setFetchingRegion(true)
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&addressdetails=1`);

        if (!response.ok) {
            setFetchingRegion(false)
            throw new Error(`HTTP error ${response.status}`)

        }
        const data = await response.json()

        const citycode = data.address?.postcode ?? null
        console.log("setting citycode to", citycode)
        setFetchingRegion(false)
        return citycode
    }

    useEffect(() => {
        async function loadRegionID() {
            if (!pickedLocation) {
                setNewFacilityRegion("")
                return;
            }
            try {
                const region = await getRegionID(Object.values(pickedLocation)[0], Object.values(pickedLocation)[1]);
                setNewFacilityRegion(region)
            }

            catch (err) {
                console.log(err);
                setNewFacilityRegion("<error>")
            }
        }
        loadRegionID()
    }, [pickedLocation])

    const handleAddFacility = async (e) => {
        e.preventDefault()
        setSubmitted(true)

        if (hasErrorID) { return }

        const payload = {
            facility_id: Number(newFacilityID),
            facility_name: newFacilityName,
            region_id: newFacilityRegion,
            resources: newResources,
            lat: Object.values(pickedLocation)[0] ?? 46.2276,
            lon: Object.values(pickedLocation)[1] ?? 2.2137,
        };

        await fetch("/api/addFacility", {
            method: "POST",
            body: JSON.stringify(payload),
            headers: { "Content-Type": "application/json" }

        })
        const res = await fetch("/api/state");
        const data = await res.json();
        setInputData(data);
        console.log(data)
        setOpenDialog(false);
        setPickedLocation(null)
    };


    return (
        <Dialog open={openDialog && !isPickingLocation} onClose={handleClose}>
            <Paper elevation={2} sx={{ p: 1, m: 0.4, width: 400, maxWidth: "100%" }}>
                <DialogTitle> Create Facility </DialogTitle>
                <form onSubmit={handleAddFacility} id="new-facility-form">
                    <Box sx={{ display: "flex", flexDirection: "column", m: 2, gap: 1 }}>
                        <Grid container alignItems="center">
                            <Grid item sx={{ width: 120 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 110 }}> Facility ID </Typography>
                            </Grid>
                            <Grid item>
                                <TextField sx={{ width: 180 }} size="small" error={hasErrorID} helperText={hasErrorID ? "Invalid Finness number" : " "} value={newFacilityID} autoFocus margin="dense" onChange={(e) => setNewFacilityID(e.target.value)} />
                            </Grid>
                        </Grid>


                        <Grid container alignItems="center">
                            <Grid item sx={{ width: 120 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center" }}> Facility Name </Typography>
                            </Grid>
                            <Grid item>
                                <TextField size="small" sx={{ width: 180 }} value={newFacilityName} helperText=" " autoFocus onChange={(e) => setNewFacilityName(e.target.value)} />
                            </Grid>
                        </Grid>




                        <Grid container alignItems="center">
                            <Grid item sx={{ width: 120 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 110 }}> Resources </Typography>
                            </Grid>
                            <Grid item sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                                <Select size="small" sx={{ width: 180 }} value={resourcesIDs.includes(selectedResourceID) ? selectedResourceID : ''} onChange={(e) => setSelectedResourceId(e.target.value)}>

                                    {resourcesIDs.map((rid) => {
                                        return (<MenuItem key={rid} value={rid}> {rid}</MenuItem>)
                                    })}
                                </Select>
                            </Grid>
                            <Grid item>
                                <Button onClick={handleAddResource}>Add</Button>
                            </Grid>
                            <Grid container direction="row" sx={{ gap: 1, width: "100%" }}>

                                {newResources.map((resource, index) => (
                                    <Grid item xs={12} sx={{ mt: 2 }} >
                                        <FacilityResourceCard key={resource.resource_id} resource={resource}
                                            updateResource={(updated) => { setNewResources(prev => prev.map(r => r.resource_id === updated.resource_id ? updated : r)) }}
                                            removeResource={(id) => { setNewResources(prev => prev.filter(r => r.resource_id != id)) }} >

                                        </FacilityResourceCard>
                                    </Grid>
                                )
                                )}
                            </Grid>
                        </Grid>



                        <Grid container direction="row" sx={{ gap: 3, mt: 4 }}>
                            <Grid item>

                                <Button onClick={() => setIsPickingLocation(true)}>Pick Location</Button>
                                {pickedLocation &&
                                    <Typography sx={{ display: "flex", gap: 3 }}> lat:
                                        {Object.values(pickedLocation)[0].toFixed(5)} lon: {Object.values(pickedLocation)[1].toFixed(5)}
                                    </Typography>
                                }
                            </Grid>
                            <Grid item  sx={{width:120}}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Region </Typography>
    
                                <TextField size="small" sx={{ flexGrow: 1 }} value={newFacilityRegion} autoFocus margin="dense" onChange={(e) => setNewFacilityRegion(e.target.value)} />
                            </Grid>
                        </Grid>

                        <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, mt: 5 }}>
                            <Button variant="contained" onClick={handleCancel}>Cancel</Button>
                            <Button variant="contained" loading={fetchingRegion} type="submit" form="new-facility-form">
                                Save
                            </Button>
                        </Box>

                    </Box>
                </form>
            </Paper>
        </Dialog>
    )
}

function FacilityResourceCard({ resource, updateResource, removeResource }) {

    return (

        <Paper key={resource.resource_id} sx={{ p: 1, display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
            <Typography sx={{ width: 100 }}>{resource.resource_id}</Typography>

            <TextField label="capacity" size="small" slotProps={{ htmlInput: { min: 0, step: 1 } }}
                type="number" value={resource.capacity} sx={{ width: 80 }}
                onChange={(e) => updateResource({ ...resource, capacity: Number(e.target.value) })} />
            <TextField label="max in" size="small" slotProps={{ htmlInput: { min: 0, max: 2, step: 0.1 } }}
                type="number" value={resource.max_transferable_in} sx={{ width: 80 }}
                onBlur={() => updateResource({ ...resource, max_transferable_in: Math.max(0, Math.min(2, Number(resource.max_transferable_in || 0))) })}
                onChange={(e) => updateResource({ ...resource, max_transferable_in: e.target.value })} />
            <TextField label="max out" size="small" slotProps={{ htmlInput: { min: 0, max: 1, step: 0.1 } }}
                type="number" value={resource.max_transferable_out} sx={{ width: 80 }}
                onBlur={() => updateResource({ ...resource, max_transferable_out: Math.max(0, Math.min(1, Number(resource.max_transferable_out || 0))) })}
                onChange={(e) => updateResource({ ...resource, max_transferable_out: e.target.value })} />
            <IconButton size="small" onClick={() => removeResource(resource.resource_id)}>
                <DeleteIcon />
            </IconButton>
        </Paper>)
}