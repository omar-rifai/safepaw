

import { Box } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid';
import { useContext } from 'react';
import { DataContext, UIContext } from '../../App';


function hasValues(resources, col) {
    return Array.isArray(resources) && resources.some(d => d[col] != null);
}


export default function ResourcesForm() {


    const { inputData, setInputData, setOutputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);
    const resources = inputData.entries?.resources || inputData.instance?.resources || [];

    const handRowUpdate = async (newRow) => {
        setOutputData({})
        console.log("in resources form", selectedFacilityID)
        const response = await fetch(`/api/update_FacilityResources`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "resource_id": newRow.resource_id, "facility_id": newRow.facility_id, "capacity": newRow.capacity })
        }).catch(console.error);

        const result = await response.json();

        setTimeout(() => {
            setInputData(prev => ({
                ...prev,
                entries: result.entries,
                facilities_capacities: result.facilities_capacities
            }));
        }, 0);

        return result.entries?.resources.find(r => r.resource_id === newRow.resource_id) ?? newRow;
    };


    const columns = [
        { field: 'facility_id', headerName: 'Facility ID', width: 130 },
        { field: 'resource_id', headerName: 'Resource ID', width: 130 },
        ...(hasValues(resources, "capacity") ? [{ field: 'capacity', headerName: 'Capacity', width: 130, editable: true, type: 'number', }] : []),
    ];

    const rows = selectedFacilityID ?
        resources.filter(r => { return r.facility_id === selectedFacilityID }) :
        resources

    function getRowId(row) {
        return (row.facility_id + row.resource_id);
    }

    return (
        <Box
            sx={{
                flexGrow: 1,
                minWidth: 0,
                width: "100%",
                ml: 5
            }}
        >
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
                onProcessRowUpdateError={console.error}
                disableRowSelectionOnClick
            />

        </Box >
    );
}