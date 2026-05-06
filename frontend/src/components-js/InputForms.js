
import './forms.css'
import { useState, useContext, } from 'react'
import { Stack, Tabs, Tab } from "@mui/material";
import { DataContext } from '../App';
import FacilitiesForm from './FacilitiesForm';
import PathwaysForm from './PathwaysForm';

import PersonalInjuryIcon from '@mui/icons-material/PersonalInjury';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import RouteIcon from '@mui/icons-material/Route';
import VaccinesIcon from '@mui/icons-material/Vaccines';
import TuneIcon from '@mui/icons-material/Tune';





export default function ManualInputForm() {
    const [activeTab, setActiveTab] = useState("tab-facilities")
    const { setOutputData } = useContext(DataContext);
    const handleChange = (_, val) => {
        setActiveTab(val);
        setOutputData(null)
    };


    return (

        <Stack >
            <Tabs value={activeTab} onChange={handleChange} variant="scrollable"
                scrollButtons="auto">
                <Tab label="Facilities" value="tab-facilities" sx={{ fontSize: 10 }} icon={<LocalHospitalIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Pathways" value="tab-pathways" sx={{ fontSize: 10 }} icon={<RouteIcon sx={{ fontSize: 20 }} />} />
                <Tab label="Patient Groups" value="tab-patients" sx={{ fontSize: 10 }} icon={<PersonalInjuryIcon sx={{ fontSize: 20 }} />} wrapped />
                <Tab label="Resources" value="tab-resources" sx={{ fontSize: 10 }} icon={<VaccinesIcon sx={{ fontSize: 20 }} />} wrapped />
                <Tab label="Instance" value="tab-instance" sx={{ fontSize: 10 }} icon={<TuneIcon sx={{ fontSize: 20 }} />} />
            </Tabs>
            {activeTab == "tab-facilities" && <FacilitiesForm />}
            {activeTab == "tab-pathways" && <PathwaysForm />}
        </Stack >
    );
}

