

import { Card } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid';
import { useContext } from 'react';
import { DataContext } from '../../App';


function hasValues(resources, col) {
    return Array.isArray(resources) && resources.some(d => d[col] != null);
}


export default function ResourcesForm({ selectedFacilityID, setInputData }) {
    const { inputData } = useContext(DataContext);
    const resources = inputData.entries?.resources || inputData.instance?.resources || [];

    const handRowUpdate = async (newRow) => {
        const response = await fetch(`/api/update_FacilityResources`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "resource_id": newRow.resource_id, "facility_id": selectedFacilityID, "capacity": newRow.capacity })
        }).catch(console.error);

        const result = await response.json();
        console.log(result.entries?.resources)
        setTimeout(() => {
            setInputData(prev => ({
                ...prev,
                entries: { ...prev.entries, resources: result.entries?.resources }
            }));
        }, 0);

        return result.entries?.resources.find(r => r.resource_id === newRow.resource_id) ?? newRow;
    };


    const columns = [{ field: 'resource_id', headerName: 'Resource ID', width: 160 },
    { field: 'transfer_unit', headerName: 'Transfer Unit', width: 100 },
    ...(hasValues(resources, "capacity") ? [{
        field: 'capacity',
        headerName: 'Capacity',
        width: 100,
        editable: true,
        type: 'number',
    }] : []),

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
                editMode='cell'
                processRowUpdate={handRowUpdate}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                onProcessRowUpdateError={console.error}
                disableRowSelectionOnClick
            />

        </Card >
    );
}