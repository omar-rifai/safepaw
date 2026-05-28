
import './forms.css'
import { useState, useContext, useEffect } from 'react'
import { Grid } from "@mui/material";
import { UIContext, DataContext } from '../App';
import FacilitiesForm from './tabs/FacilitiesForm';
import PathwaysForm from './tabs/PathwaysForm';
import ResourcesForm from './tabs/ResourcesForm';
import PatientsGroupForm from './tabs/PatientsGroupForm'
import ConfigForm from './tabs/ConfigForm';



export default function ManualInputForm({activeTab}) {
    console.log("active tab",activeTab)
    return (
        <Grid container sx={{height:"50%", flexGrow: 1, alignItems:"right", minWidth: 0, width: "95%",mt:10}}>
            {activeTab == "tab-facilities" && <FacilitiesForm />}
            {activeTab == "tab-pathways" && <PathwaysForm />}
            {activeTab == "tab-resources" && <ResourcesForm/>}
            {activeTab == "tab-patients" && <PatientsGroupForm />}
            {activeTab == "tab-instance" && <ConfigForm />}
        </Grid >
    );
}

