import { Tabs, Tab, Box } from '@mui/material';
import JsonInputForm from "./InputJsonForm.js"
import ManualInputForm from "./InputManualForm.js"
import {  useState, useContext } from "react";
import { DataContext } from "../App.js";


export default function inputForms() {

    const {setOutputData } = useContext(DataContext);

    const [activeTab, setActiveTab] = useState("manual")
    const handleChange = (_, val) => {
        setActiveTab(val);
        setOutputData (null)
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', ml:2 }}>
            <Tabs value={activeTab} onChange={handleChange}>
                <Tab label="Manual" value="manual"></Tab>
                <Tab label="Custom" value="custom"></Tab>
            </Tabs>

            <Box sx={{ flex: 1, overflowY: 'auto', pr: 3 }}>
                {activeTab === "custom" && 
                    <JsonInputForm/>
                }
                { activeTab === "manual" &&
                    <ManualInputForm/>
                }
            </Box>

        </Box>
    );

}