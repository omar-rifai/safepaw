
import { DataGrid } from '@mui/x-data-grid';
import { Card } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../App';

export default function PathwaysForm() {
    const { inputData } = useContext(DataContext);

    const columns = [{ field: 'facility_id', headerName: 'ID', width: 150 },
    { field: 'facility_type', headerName: 'Type', width: 90, editable: true }];


    const rows = inputData.instance.facilities

    function getRowId(row) {
        return row.facility_id;
    }

    return (
        < Card sx={{ m: 5 }}>

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