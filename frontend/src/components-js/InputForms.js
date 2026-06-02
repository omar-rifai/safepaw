
import './forms.css'
import { Grid } from "@mui/material";
import FacilitiesForm from './tabs/FacilitiesForm';
import PathwaysForm from './tabs/PathwaysForm';
import ResourcesForm from './tabs/ResourcesForm';

import ConfigForm from './tabs/ConfigForm';



export default function DataGridForm({activeTab}) {
    return (
        <Grid container sx={{height:"50%", flexGrow: 1, alignItems:"right", minWidth: 0, width: "95%",mt:10}}>
            {activeTab == "tab-facilities" && <FacilitiesForm />}
            {activeTab == "tab-pathways" && <PathwaysForm />}
            {activeTab == "tab-resources" && <ResourcesForm/>}
            {activeTab == "tab-instance" && <ConfigForm />}
        </Grid >
    );
}

