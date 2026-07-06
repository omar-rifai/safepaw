import { Box, Card, CardContent, Stack, Chip, Button, Typography } from "@mui/material"
import { DataContext, UIContext } from "../App";
import { useContext, useEffect, useState } from "react";


export default function JobsForm() {

    const { setInputData, setOutputData, inputData, isLoading, setIsLoading } = useContext(DataContext);
    const { setOpenJobsPanel } = useContext(UIContext);
    const [loadingJobID, setLoadingJobID] = useState(null)
    const [isDeleting, setIsDeleting] = useState(false)


    const statusColors = {
        Optimal: "success",
        Generating: "warning",
        Running: "warning",
        Infeasible: "error",
        Failed: "error"
    }


    useEffect(() => {
        const interval = setInterval(async () => {
            const res = await fetch("/api/get_state");
            const data = await res.json();

            setInputData(data);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    const retrieveJob = async (job_id) => {
        setLoadingJobID(job_id)
        setIsLoading(true)
        const retrieve_response = await fetch(`/api/retrieve_job/${job_id}`, {
            method: "GET",
            headers: { "Content-Type": "application/json" }
        })

        if (!retrieve_response.ok) {
            console.log("not setting InputData")
            alert("No data to display.");
            setLoadingJobID(null)
            setIsLoading(false)
            return
        }

        const payload_retrieve = await retrieve_response.json()
        if (payload_retrieve["status"] == "Infeasible") {
            setInputData(payload_retrieve["input_data"])
            setOutputData({})
            return
        }
        console.log("setting output data to:", payload_retrieve["output_data"])
        setOutputData(payload_retrieve["output_data"])
        setInputData(payload_retrieve["input_data"])
        setIsLoading(false)
        setOpenJobsPanel(false)
        console.log("in jobs forms after retrieve job, inputData:", payload_retrieve["input_data"])
    }


    async function loadState() {
        const res = await fetch("/api/get_state");
        const data = await res.json()
        setInputData(data)
    }

    async function deleteJob(job_id) {
        if (!job_id) return;
        setIsDeleting(true)
        await fetch(`/api/deleteJob/${job_id}`, { method: "DELETE" })
        loadState()
        setIsDeleting(false)
    }

    return (
        <Box sx={{ width: 350, p: 2 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
                Jobs
            </Typography>

            {inputData.jobs?.map((job) => (
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
                            <Button size="small" variant="text" onClick={() => retrieveJob(job.id)} loading={loadingJobID == job.id}> Load </Button>
                            <Button size="small" variant="text" loading={isDeleting} onClick={() => deleteJob(job.id)}> Delete </Button>
                        </Stack>

                    </CardContent>
                </Card>
            ))}
        </Box>
    )
}