import { DataGrid } from '@mui/x-data-grid';
import { useCallback, useMemo } from 'react';

import { Box, Grid, Button, Dialog, Typography, Card, TextField } from '@mui/material'
import { useContext, useState, useEffect } from 'react';
import { DataContext, UIContext } from '../../App';

export default function FacilitiesForm() {
    const [openDialog, setOpenDialog] = useState(false)
    const [newFacilityName, setNewFacilityName] = useState(null)
    const [newFacilityID, setNewFacilityID] = useState(null)


    const { inputData, setInputData } = useContext(DataContext);
    const { selectedFacilityID, setSelectedFacilityID, isPickingLocation, setIsPickingLocation } = useContext(UIContext);

    const facilities = inputData.entries?.facilities || [];

    const handleRowSelectionModelChange = useCallback((newModel) => {
        setSelectedFacilityID([...newModel.ids][0])
    }, []);

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null);
    }
    const openCreateDialog = function () {
        setOpenDialog(true)
        //setIsPickingLocation(true)
    }

    useEffect(() => {
        console.log("isPickingLocation changed:", isPickingLocation);
    }, [isPickingLocation]);
    const handleClose = () => {
        setOpenDialog(false);
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


    const columns = useMemo(() => (
        [
            { field: 'facility_id', headerName: 'ID', width: 100 },
            ...(hasValues(facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 300, editable: false, hideable: false }] : []),
            { field: '__selected', valueGetter: (_, row) => (selectedFacilityID == row.facility_id ? 1 : 0), headerName: 'Selected' },
        ]), [selectedFacilityID, facilities]);

    const rows = facilities

    function getRowId(row) {
        return row.facility_id;
    }

    return (
        <Box
            sx={{
                flexGrow: 1,
                minWidth: 0,
                width: "100%",
                ml: 5
            }}
        >
            <Button size="small" onClick={openCreateDialog}>
                Create a Facility
            </Button>
            <DataGrid
                rows={rows}
                columns={columns}
                columnVisibilityModel={{ __selected: false, facility_name: true }}
                initialState={{ pagination: { paginationModel: { pageSize: 5 } } }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                onRowSelectionModelChange={handleRowSelectionModelChange}
                rowSelectionModel={{ ids: new Set([selectedFacilityID]), type: 'include' }}
            />


            <Dialog open={openDialog} onClose={handleClose}>
                <Card sx={{ p: 3 }}>
                    <Grid sx={{ mb: 5 }}>
                        <Typography variant="h6">Create Facility</Typography>
                    </Grid>
                    <form onSubmit={handleAddFacility} id="new-facility-form">
                        <Box sx={{ display: "flex", flexDirection: "column", m: 2, gap: 1 }}>
                            <Grid container direction="row" sx={{ gap: 3 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width:100}}> Facility ID </Typography>
                                <TextField autoFocus margin="dense"  onChange={(e) => setNewFacilityID(e.target.value)} type="number" />
                            </Grid>
                            <Grid container direction="row" sx={{ gap: 3 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width:100}}> Facility Name </Typography>
                                <TextField autoFocus margin="dense"  onChange={(e) => setNewFacilityName(e.target.value)}  />
                            </Grid>
                            <Grid container direction="row" sx={{ gap: 3 }}>
                                <Typography sx={{ display: "flex", flexDirection: "column", justifyContent: "center", width:100}}> Facility Name </Typography>
                                <TextField autoFocus margin="dense"  onChange={(e) => setNewFacilityName(e.target.value)}  />
                            </Grid>
                            <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, mt: 2 }}>
                                <Button onClick={handleClose}>Cancel</Button>
                                <Button type="submit" form="new-facility-form">
                                    Save
                                </Button>
                            </Box>

                        </Box>
                    </form>
                </Card>
            </Dialog>
        </Box>
    );
}

