
import { DataGrid } from '@mui/x-data-grid';
import { Card } from '@mui/material'
import { useContext, useEffect } from 'react';
import { DataContext } from '../App';

export default function FacilitiesForm() {
    const { inputData } = useContext(DataContext);

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null)
    }

    const columns = [{ field: 'facility_id', headerName: 'ID', width: 100 },
    ...hasValues(inputData.instance?.facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 200, editable: true }] : [],
    ...hasValues(inputData.instance?.facilities, "facility_type") ? [{ field: 'facility_type', headerName: 'Type', width: 60, editable: true }] : [],
    ];


    const rows = inputData.instance?.facilities

    function getRowId(row) {
        return row.facility_id;
    }

    return (
        < Card>

            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 5,
                        },
                    },
                }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                disableRowSelectionOnClick
            />

        </Card >
    );
}