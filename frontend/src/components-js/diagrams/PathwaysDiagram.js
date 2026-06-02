
import { Stack, Typography } from '@mui/material';
import { DataContext } from '../../App';
import { useContext, useMemo } from "react";
import MermaidDiagram from "./MermaidDiagram";


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
        "graph TD\n" +
        `START((Start)) --> ${activities.join(" --> ")} --> END((End))`;

    return (
        <Stack container direction="column" alignItems="center" sx={{ width: "95%" }}>
            <Typography>Patients Pathway</Typography>
            <MermaidDiagram chart={chart} />
        </Stack>
    );
}

