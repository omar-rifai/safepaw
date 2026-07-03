
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
    const chart =
        [
            "graph TD",
            "START((Start))",
            "END((End))",
            ...activities.map((a, i) => `A${i}["${String(a)}"]`),
            "START --> A0",
            ...activities.slice(1).map((_, i) => `A${i} --> A${i + 1}`),
            `A${activities.length - 1} --> END`,
        ].join("\n");
    return (
        <Stack container direction="column" alignItems="center" sx={{ width: "95%", height:300 }}>
            <Typography>Patients Pathway</Typography>
            <FlowDiagram />
        </Stack>
    );
}

