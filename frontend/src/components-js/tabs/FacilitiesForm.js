import { DataGrid } from '@mui/x-data-grid';
import { Card } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../../App';

export default function FacilitiesForm() {
    const { inputData, setInputData } = useContext(DataContext);
    const facilities = inputData.entries?.facilities || inputData.instance?.facilities || [];

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null);
    }

    const columns = [
        { field: 'facility_id', headerName: 'ID', width: 100 },
        ...(hasValues(facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 300, editable: false }] : []),
    ];

    const rows = facilities || [];

    function getRowId(row) {
        return row.facility_id;
    }

    return (
        <Card>
            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{ pagination: { paginationModel: { pageSize: 5 } } }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                disableRowSelectionOnClick
            />
        </Card>
    );
}