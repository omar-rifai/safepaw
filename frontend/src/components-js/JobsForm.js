import { Box, Card, CardContent, Stack, Chip, Button, Typography } from "@mui/material"
import { DataContext } from "../App";
import { useContext } from "react";


export default function JobsForm({ jobs_list }) {

    const { setInputData, setOutputData, setIsOptimizing} = useContext(DataContext);

    const statusColors = {
        Finished: "success",
        Running: "warning",
        Infeasible: "error"
    }


    const retrieveJob = async (job_id) => {
        const retrieve_response = await fetch(`/api/retrieve_job/${job_id}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        })

        if (!retrieve_response.ok) {
            const error = await retrieve_response.json()
            alert(error.detail);
            setIsOptimizing(false)
            return
        }

        const payload_retrieve = await retrieve_response.json()
        if (payload_retrieve["status"] == "Infeasible") {
            alert("Could not optimize instance. Please modify instance parameters and try again.")
            setIsOptimizing(false)
            return
        }

        setOutputData(payload_retrieve)
    }

    async function loadState() {
        const res = await fetch("/api/get_state");
        const data = await res.json()
        setInputData(data)
    }

    async function deleteJob(job_id) {
        if (!job_id) return;
        await fetch(`/api/deleteJob/${job_id}`, { method: "DELETE" })
        loadState()
    }

    return (
        <Box sx={{ width: 350, p: 2 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
                Jobs
            </Typography>

            {jobs_list.map((job) => (
                <Card variant="outlined" sx={{ mb: 1 }}>
                    <CardContent sx={{ p: 1.5, "&:last-child": { pb: 1.5 } }}>

                        <Stack direction="row" justifyContent="space-between">
                            <Typography variant="subtitle2" sx={{ width: 180 }}>
                                Job #{job.id}
                            </Typography>

                            <Chip
                                size="small"
                                label={job.status}
                                color={statusColors[job.status]}
                            />
                        </Stack>

                        <Typography variant="body2">
                            Dataset type: {job.mode}
                        </Typography>
                        <Typography variant="body2">
                            Department code: {job.dep_code}
                        </Typography>

                        <Stack direction="row" justifyContent="flex-end" sx={{ mt: 1, gap: 1 }}>
                            <Button size="small" variant="text" onClick={() => retrieveJob(job.id)}> Load </Button>
                            <Button size="small" variant="text" onClick={() => deleteJob(job.id)}> Delete </Button>
                        </Stack>

                    </CardContent>
                </Card>
            ))}
        </Box>
    )
}