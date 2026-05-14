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

    const facilityTypeOptions = [...new Set(
        facilities.map(f => f.facility_type).filter(v => v != null)
    )];

    const handRowUpdate = async (newRow) => {
        const response = await fetch(`/api/update_facility/${newRow.facility_id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ facility_type: newRow.facility_type })
        }).catch(console.error);

        const result = await response.json();

        setTimeout(() => {
            setInputData(prev => ({
                ...prev,
                entries: { ...prev.entries, facilities: result.entries?.facilities }
            }));
        }, 0);

        return result.entries?.facilities.find(f => f.facility_id === newRow.facility_id) ?? newRow;
    };

    const columns = [
        { field: 'facility_id', headerName: 'ID', width: 100 },
        ...(hasValues(facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 300, editable: false }] : []),
        ...(hasValues(facilities, "facility_type") ? [{
            field: 'facility_type',
            headerName: 'Type',
            width: 100,
            editable: true,
            type: 'singleSelect',
            valueOptions: facilityTypeOptions,
        }] : []),
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
                editMode='cell'
                processRowUpdate={handRowUpdate}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                onProcessRowUpdateError={console.error}
                disableRowSelectionOnClick
            />
        </Card>
    );
}