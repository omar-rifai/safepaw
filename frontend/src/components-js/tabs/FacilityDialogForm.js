import { Box, Button, Dialog, IconButton, DialogTitle, Typography, Paper, Grid, TextField, Select, MenuItem } from "@mui/material"
import { useContext, useState, useEffect } from 'react';
import { UIContext, DataContext } from '../../App';
import DeleteIcon from "@mui/icons-material/Delete";

export default function FacilityDialog({ openDialog, setOpenDialog }) {

    const { inputData, setInputData } = useContext(DataContext)
    const { isPickingLocation, setIsPickingLocation, pickedLocation, setPickedLocation } = useContext(UIContext);
    const [newFacilityName, setNewFacilityName] = useState(null)
    const [newFacilityID, setNewFacilityID] = useState(null)
    const [selectedResourceID, setSelectedResourceId] = useState(null)
    const [resourcesIDs, setResourcesIDs] = useState([]);
    const [newResources, setNewResources] = useState([]);

    const handleAddResource = () => {
        console.log("here we are")
        setNewResources([...newResources, { resource_id: selectedResourceID, capacity: 0, max_transferable_in: 0, max_transferable_out: 0 }])
    }

    const handleClose = () => {
        setOpenDialog(false);
    };

    const handleCancel = () => {
        setOpenDialog(false);
        setPickedLocation(null)
    };

    useEffect(() => {
        const unique_resources = [...new Set(inputData.entries?.resources.map((e) => e.resource_id))] ?? []
        setResourcesIDs(unique_resources)
    }, [inputData])

    const handleAddFacility = async (e) => {

        e.preventDefault()
        const payload = {
            facility_id: Number(newFacilityID),
            facility_name: newFacilityName,
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
    };
    return (
        <Dialog open={openDialog && !isPickingLocation} onClose={handleClose}>
            <Paper elevation={2} sx={{ p: 1, m: 0.4, width: 400, maxWidth: "100%" }}>
                <DialogTitle> Create Facility </DialogTitle>
                <form onSubmit={handleAddFacility} id="new-facility-form">
                    <Box sx={{ display: "flex", flexDirection: "column", m: 2, gap: 2 }}>
                        <Grid container direction="row" sx={{ gap: 3 }}>
                            <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Facility ID </Typography>
                            <TextField sx={{ flexGrow: 1 }} autoFocus margin="dense" onChange={(e) => setNewFacilityID(e.target.value)} type="number" />
                        </Grid>
                        <Grid container direction="row" sx={{ gap: 3 }}>
                            <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Facility Name </Typography>
                            <TextField sx={{ flexGrow: 1 }} autoFocus margin="dense" onChange={(e) => setNewFacilityName(e.target.value)} />
                        </Grid>
                        <Grid container direction="row" sx={{ display: "flex", mt: 2, gap: 2 }}>
                            <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Resources </Typography>

                            <Select sx={{ flexGrow: 1 }} value={selectedResourceID} onChange={(e) => setSelectedResourceId(e.target.value)}>
                                {resourcesIDs.map((rid) => {
                                    return (<MenuItem key={rid} value={rid}> {rid}</MenuItem>)
                                })}
                            </Select>
                            <Button onClick={handleAddResource}>Add</Button>

                            <Grid container direction="row" sx={{ gap: 1, width: "100%" }}>
                                {newResources.map((resource, index) => (
                                    <FacilityResourceCard key={resource.resource_id} resource={resource}
                                        updateResource={(updated) => { setNewResources(prev => prev.map(r=> r.resource_id === updated.resource_id? updated: r)) }}
                                        removeResource={(id)=> {setNewResources(prev=>prev.filter(r=> r.resource_id != id))}} >

                                    </FacilityResourceCard>
                                )
                                )}
                            </Grid>
                        </Grid>
                        <Grid container direction="row" >
                            <Button onClick={() => setIsPickingLocation(true)}>Pick Location</Button>
                            {pickedLocation && <Typography> {Object.values(pickedLocation)}</Typography>}
                        </Grid>


                        <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, mt: 5 }}>
                            <Button onClick={handleCancel}>Cancel</Button>
                            <Button type="submit" form="new-facility-form">
                                Save
                            </Button>
                        </Box>

                    </Box>
                </form>
            </Paper>
        </Dialog>
    )
}

function FacilityResourceCard({resource, updateResource, removeResource}) {

    return (

        <Paper key={resource.resource_id} sx={{ p: 1, display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
            <Typography sx={{ width: 100 }}>{resource.resource_id}</Typography>

            <TextField label="capacity" size="small" type="number" value={resource.capacity} sx={{ width: 80 }}
                onChange={(e) => updateResource({ ...resource, capacity: Number(e.target.value) })} />
            <TextField label="max in" size="small" type="number" value={resource.max_transferable_in} sx={{ width: 80 }}
                onChange={(e) => updateResource({ ...resource, max_transferable_in: Number(e.target.value) })} />
            <TextField label="max out" size="small" type="number" value={resource.max_transferable_out} sx={{ width: 80 }}
                onChange={(e) => updateResource({ ...resource, max_transferable_out: Number(e.target.value) })} />
            <IconButton size="small" onClick={() => removeResource(resource.resource_id)}>
                <DeleteIcon />
            </IconButton>
        </Paper>)
}