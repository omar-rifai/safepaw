

import { Card } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid';
import { useContext } from 'react';
import { DataContext } from '../../App';



export default function PatientsGroupForm() {

    function hasValues(groups, col) {
        return Array.isArray(groups) && groups.some(d => d[col] != null)
    }

    const { inputData } = useContext(DataContext);
    const groups = inputData.entries?.patients_groups || inputData.instance?.patients_groups || [];
    const columns = [{ field: 'group_id', headerName: 'Group ID', width: 130 },
    ...hasValues(groups, "lbl") ? [{ field: 'lbl', headerName: 'Label', width: 200, editable: false }] : [],
    { field: 'pathways', headerName: 'Pathways', width: 300, }
    ];


    const rows = groups

    function getRowId(row) {
        return (row.group_id);
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