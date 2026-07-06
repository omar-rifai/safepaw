
import { Stack, Typography } from '@mui/material';
import { DataContext } from '../../App';
import { useContext, useMemo } from "react";
import FlowDiagram from "./FlowDiagram";


export default function PathwaysChart() {

    const { inputData, selectedPathwayID } = useContext(DataContext);
    const pathways = inputData?.entries?.pathways ? inputData.entries.pathways :
        null

    const selectedPathway = useMemo(() => {
        if (!pathways?.length) return null;
        return selectedPathwayID ? pathways
            .find((e) => String(e.pathway_id) + String(e.group_id) === String(selectedPathwayID)) : pathways[0]
    }, [selectedPathwayID, pathways])


    const activities = selectedPathway?.activities ?? []

    return (
        <Stack direction="column" alignItems="center" sx={{ width: "95%", height: "100%", minHeight: 0 }}>
            <Typography>Patients Pathway</Typography>
            <div style={{ width: '100%', height:"100%", flex: 1, minHeight: 0 }}>
                <FlowDiagram activities={activities} />
            </div>
        </Stack>
    );
}

