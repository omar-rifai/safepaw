
import { DataGrid, useGridApiContext } from '@mui/x-data-grid';
import { Card } from '@mui/material'
import { useContext } from 'react';
import { DataContext } from '../../App';
import Select from '@mui/material/Select';

export default function FacilitiesForm() {
    const { inputData, setInputData } = useContext(DataContext);

    function hasValues(facilities, col) {
        return Array.isArray(facilities) && facilities.some(d => d[col] != null)
    }

    const facilityTypeOptions = [...new Set((inputData.instance?.facilities.map
        (f => f.facility_type)
        .filter(v => v != null)
    ))];


    const handRowUpdate = async (newRow, oldRow) => {

        const updatedResources = { ...(oldRow.resources_capacity || {}), };
        Object.keys(newRow).forEach(key => {
            if (key in updatedResources) {
                updatedResources[key] = newRow[key];
            }
        });

        const updated_row = { ...oldRow, facility_type: newRow.facility_type};

        const response = await fetch("/api/facilities/" + updated_row.facility_id, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                "facilities": inputData.instance.facilities,
                "updated": updated_row,
                "mode": inputData.instance.instance.mode
            })
        })
            .catch(console.error);

        const result = await response.json();
        console.log("result.facilities:", result.facilities);

        setInputData(prev => {
            const next = { ...prev, instance: { ...prev.instance, facilities: result.facilities } };
            return next;
        });
        return result.facilities.find(f => f.facility_id === updated_row.facility_id) ?? updated_row;

    }

    function typeEditCellComponent(props) {
        const { id, value, field } = props;
        const apiRef = useGridApiContext();

        const handleChange = async (event) => {
            await apiRef.current.setEditCellValue({ id, field, value: event.target.value });
            apiRef.current.stopCellEditMode({ id, field });
        };

        return (
            <Select
                value={value}
                onChange={handleChange}
                size="small"
                sx={{ height: 1 }}
                native
                autoFocus
            >
                {facilityTypeOptions.map(option => (
                    <option key={option} value={option}>
                        {option}
                    </option>
                ))}
            </Select>
        );
    }

    const columns = [{ field: 'facility_id', headerName: 'ID', width: 100 },
    ...hasValues(inputData.instance?.facilities, "facility_name") ? [{ field: 'facility_name', headerName: 'Name', width: 300, editable: false }] : [],
    ...hasValues(inputData.instance?.facilities, "facility_type") ? [{
        field: 'facility_type', headerName: 'Type', width: 60, editable: true, renderEditCell: typeEditCellComponent
    }] : [],
    ];

    const rows = inputData.instance?.facilities || [];

    function getRowId(row) {
        return row.facility_id;
    }


    return (
        < Card>

            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{ pagination: { paginationModel: { pageSize: 5 } } }}
                processRowUpdate={handRowUpdate}
                getRowId={getRowId}
                pageSizeOptions={[5]}
                checkboxSelection
                disableRowSelectionOnClick
            />

        </Card >
    );
}