

import { Card } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid';
import { useContext } from 'react';
import { DataContext, UIContext } from '../../App';



export default function PatientsGroupForm() {

    function hasValues(groups, col) {
        return Array.isArray(groups) && groups.some(d => d[col] != null)
    }

    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);

    const groups = inputData.entries?.patients_groups || inputData.instance?.patients_groups || [];
    const columns = [
        { field: 'group_id', headerName: 'Group ID', width: 130 },
        ...hasValues(groups, "lbl") ? [{ field: 'lbl', headerName: 'Label', width: 200, editable: false }] : [],
        { field: 'pathways', headerName: 'Pathways', width: 300, }
    ];


    const rows = selectedFacilityID ?
        groups.filter(g => { return g.facility_id === selectedFacilityID }) :
        groups


     const unique_rows = rows.filter((row, i, self) => i === self.findIndex(
        r => r.group_id === row.group_id && JSON.stringify(r.pathways) === JSON.stringify(row.pathways) )
    )
    
    
    function getRowId(row) {
        return (row.facility_id + row.group_id);
    }

    return (
        < Card>

            <DataGrid
                rows={unique_rows}
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