import { DataGrid } from '@mui/x-data-grid';
import { useCallback, useMemo } from 'react';
import { Box, Button } from '@mui/material'
import { useContext, useState, useEffect } from 'react';
import { DataContext, UIContext } from '../../App';
import FacilityDialog from './FacilityDialogForm';

export default function FacilitiesForm() {
    const [openDialog, setOpenDialog] = useState(false)

    const { inputData, setInputData, setOutputData} = useContext(DataContext);
    const { selectedFacilityID, setSelectedFacilityID } = useContext(UIContext);

    const openCreateDialog = function () {
        setOutputData({})
        setOpenDialog(true)
    }

    const rowSelectionModel = useMemo(() => ({
        ids: selectedFacilityID == null ? new Set() : new Set([selectedFacilityID]),
        type: 'include',
    }), [selectedFacilityID]);

    const facilities = inputData.entries?.facilities || [];

    const handleRowSelectionModelChange = useCallback((newModel) => {
        setSelectedFacilityID([...newModel.ids][0])
    }, []);

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null);
    }


    async function loadState() {
        const res = await fetch("/api/state");
        const data = await res.json()
        setInputData(data)
    }

    const deleteFacility = async (facility_id) => {
        if (!facility_id) return;
        await fetch(`/api/deleteFacility/${facility_id}`, { method: "DELETE" })
        loadState()
        setOutputData({})
    }

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
        <Box sx={{ flexGrow: 1, minWidth: 0, width: "100%", ml: 5 }}>
            <DataGrid
                rows={rows}
                columns={columns}
                columnVisibilityModel={{ __selected: false, facility_name: true }}
                initialState={{ pagination: { paginationModel: { pageSize: 5 } } }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                onRowSelectionModelChange={handleRowSelectionModelChange}
                rowSelectionModel={rowSelectionModel}
            />
            <FacilityDialog openDialog={openDialog} setOpenDialog={setOpenDialog} />

            <Button size="small" onClick={openCreateDialog}>Create </Button>
            <Button size="small" onClick={() => deleteFacility(selectedFacilityID)}>Delete </Button>
        </Box>
    );
}

