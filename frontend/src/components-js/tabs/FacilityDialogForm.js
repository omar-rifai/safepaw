import { Box, Button, Dialog, IconButton, DialogTitle, Typography, Paper, Grid, TextField, Select, MenuItem } from "@mui/material"
import { useContext, useState, useEffect } from 'react';
import { UIContext } from '../../App';
import DeleteIcon from "@mui/icons-material/Delete";

export default function FacilityDialog({ openDialog, setOpenDialog }) {


    const { isPickingLocation, setIsPickingLocation, pickedLocation, setPickedLocation } = useContext(UIContext);
    const [newFacilityName, setNewFacilityName] = useState(null)
    const [newFacilityID, setNewFacilityID] = useState(null)
    const [newFacilityType, setNewFacilityType] = useState(null)
    const [selectedResourceID, setSelectedResourceId] = useState(null)
    const [resourcesData, setResourcesData] = useState([
        { id: 0, label: 'Bed/days', capacity: 0 },
        { id: 1, label: 'Physicians', capacity: 0 },
    ]);


    const handleClose = () => {
        setOpenDialog(false); 
    };

    const handleCancel = () => {
        setOpenDialog(false); 
        setPickedLocation(null)
    };

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
                        <Grid container direction="row" sx={{ gap: 3 }}>
                            <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Facility Type </Typography>
                            <Select sx={{ flexGrow: 1 }} />
                        </Grid>
                        <Grid container direction="row" sx={{ display: "flex", mt: 2, gap: 2 }}>
                            <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width: 100 }}> Resources </Typography>

                            <Select sx={{ flexGrow: 1 }} value={selectedResourceID} onChange={(e) => setSelectedResourceId(e.target.value)}>
                                {resourcesData.map((resource) => {
                                    return (<MenuItem key={resource.id} value={resource.id}> {resource.label}</MenuItem>)
                                })}
                            </Select>
                            <Button>Add</Button>

                            <Grid container direction="row" sx={{ gap: 1, width: "100%" }}>
                                {resourcesData.map((data) => {
                                    return (FacilityResourceCard(data));
                                })
                                }
                            </Grid>
                        </Grid>
                        <Grid container direction="row" >
                            <Button onClick={()=>setIsPickingLocation(true)}>Pick Location</Button>
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

function FacilityResourceCard(resources) {
    return (

        <Paper key={resources.id} sx={{ p: 1, display: "flex", alignItems: "center", gap: 1, width: "100%" }}>
            <Typography sx={{ width: 100 }}>{resources.label}</Typography>

            <TextField label="capacity" size="small" type="number" value={resources.capacity}
                onChange={(e) => updateResource(resources.id, { capacity: Number(e.target.value) })} sx={{ width: 80 }} />
            <TextField label="max in" size="small" type="number" value={resources.capacity}
                onChange={(e) => updateResource(resources.id, { capacity: Number(e.target.value) })} sx={{ width: 80 }} />
            <TextField label="max out" size="small" type="number" value={resources.capacity}
                onChange={(e) => updateResource(resources.id, { capacity: Number(e.target.value) })} sx={{ width: 80 }} />
            <IconButton size="small" onClick={() => removeResource(resources.id)}>
                <DeleteIcon />
            </IconButton>
        </Paper>)
}