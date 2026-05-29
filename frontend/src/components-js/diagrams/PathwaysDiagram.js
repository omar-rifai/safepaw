import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea, } from "recharts";
import { Stack, Typography } from '@mui/material';
import { DataContext, UIContext } from '../../App';
import { useContext } from "react";
import MermaidDiagram from "./MermaidDiagram";


export default function PathwaysChart() {

    const { inputData } = useContext(DataContext);
    const { selectedFacilityID } = useContext(UIContext);

    const pathways = inputData?.entries?.pathways ? inputData.entries.pathways :
        null

    const pathways_unique = pathways.filter((obj1, i, arr) =>
        arr.findIndex(obj2 => ['facility_id', 'pathway_id'].every(key => obj2[key] === obj1[key])
        ) === i)

    const selectedPathways = pathways_unique
        .filter((e) => e.facility_id === selectedFacilityID)
        .map((e) => e.pathway_id);

    console.log("in pathwayDiagrams unique pathways:", pathways_unique)
    const arr = pathways_unique[0]["activities"]
    const chart =
        "graph TD\n" +
        `START((Start)) --> ${arr.join(" --> ")} --> END((End))`;

    return (
        <Stack container direction="column" alignItems="center" sx={{ width: "95%" }}>
            <Typography>Patients Pathway</Typography>
            <MermaidDiagram chart={chart} />
        </Stack>
    );
}

