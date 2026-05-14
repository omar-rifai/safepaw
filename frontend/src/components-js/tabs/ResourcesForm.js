

import { Card } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid';
import { useContext } from 'react';
import { DataContext } from '../../App';


function hasValues(resources, col) {
    return Array.isArray(resources) && resources.some(d => d[col] != null);
}

export default function ResourcesForm() {
    const { inputData } = useContext(DataContext);
    const resources = inputData.entries?.resources || inputData.instance?.resources || [];
    const columns = [{ field: 'resource_id', headerName: 'Resource ID', width: 160 },
    ...(hasValues(resources, "capacity") ? [{ field: 'capacity', headerName: 'Capacity', width: 200, editable: false }] : []),
    { field: 'transfer_unit', headerName: 'Transfer Unit', width: 100 },
    ];


    const rows = resources

    function getRowId(row) {
        return (row.resource_id);
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