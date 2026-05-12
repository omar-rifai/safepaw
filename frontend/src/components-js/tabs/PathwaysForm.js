
import { DataGrid } from '@mui/x-data-grid';
import { Card } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../../App';

export default function PathwaysForm() {
    const { inputData } = useContext(DataContext);
    const pathways = inputData.entries?.pathways || inputData.instance?.pathways || [];
    const columns = [{ field: 'pathway_id', headerName: 'Pathway ID', width: 130 }, { field: 'group_id', headerName: 'Patients Group' },
    { field: "activities", headerName: "Activities List", width: 400 }
    ];


    const rows = pathways

    function getRowId(row) {
        return (row.pathway_id + row.associated_group_id);
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