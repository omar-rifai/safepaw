
import { DataGrid } from '@mui/x-data-grid';
import { Box } from '@mui/material'
import { useContext } from 'react';
import { DataContext, UIContext } from '../../App';

export default function PathwaysForm() {


    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);
    const pathways = inputData.entries?.pathways || inputData.instance?.pathways || [];
    const columns = [
        { field: 'pathway_id', headerName: 'Pathway ID', width: 140},
        { field: 'group_id', headerName: 'Patients Group', width: 140},
        { field: "activities", headerName: "Activities List", width: 280 }
    ];

    const rows = selectedFacilityID ?
        pathways.filter(p => { return p.facility_id === selectedFacilityID }) :
        pathways


    const unique_rows = rows.filter((row, i, self) => i === self.findIndex(
        r => r.pathway_id === row.pathway_id && r.pathway_id === row.pathway_id && r.group_id === row.group_id)
    )

    function getRowId(row) {
        return (row.facility_id + row.pathway_id + row.group_id);
    }

    return (
        <Box sx={{flexGrow: 1, minWidth: 0, width: "100%", ml: 2}}>

            <DataGrid
                rows={unique_rows}
                columns={columns}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 15,
                        },
                    },
                }}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                disableRowSelectionOnClick
            />

        </Box >
    );
}