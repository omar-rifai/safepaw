import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { Typography, TextField, Accordion, AccordionSummary, AccordionDetails, Grid } from "@mui/material"

export function getInitialNodes(activities) {

    const initialNodes = activities.map((a, index) => (
        {
            id: a.id,
            position: { x: 0, y: index * 140 },
            type: "activity-node",
            data: { activity: a },
        }
    ));

    return initialNodes
}

function ActivityNode({ data }) {
    const { activity } = data
    return (
        <>   
            <div className="react-flow__node-default">
                {<Typography> {activity?.id} </Typography>}
                <Accordion>
                    <AccordionSummary>Resources</AccordionSummary>
                    <AccordionDetails>
                        <Grid container sx={{ gap: 1 }}>
                            {activity.resources.filter((r) => (r.required_capacity != 0)).map((r) => (
                                < TextField size="small" label={r.id} value={r.required_capacity}></TextField >
                            ))}
                        </Grid>
                    </AccordionDetails>
                </Accordion>
                <Handle type="target" position={Position.Top} />
                <Handle type="source" position={Position.Bottom} />
            </div >
        </>

    );
}


export const nodeTypes = {
    "activity-node": ActivityNode,
};
