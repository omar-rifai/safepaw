import { DataGrid } from '@mui/x-data-grid';
import { RichTreeView } from '@mui/x-tree-view/RichTreeView';

import { Box } from '@mui/material'
import { useContext } from 'react';
import { DataContext, UIContext } from '../../App';

export default function FacilitiesForm() {
    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);

    const facilities = inputData.entries?.facilities || [];

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null);
    }

    const columns = [
        { field: 'facility_id', headerName: 'ID', width: 100 },
        ...(hasValues(facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 300, editable: false }] : []),
    ];

    const rows = selectedFacilityID ?
        facilities.filter(f => { return f.facility_id === selectedFacilityID }) :
        facilities

    function getRowId(row) {
        return row.facility_id;
    }

    return (
        <Box
            sx={{
                flexGrow: 1,
                minWidth: 0,
                width: "100%",
                ml:2
            }}
        >
            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{ pagination: { paginationModel: { pageSize: 5 } } }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                disableRowSelectionOnClick
            />
        </Box>
    );
}

