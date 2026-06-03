
import './forms.css'
import { Grid, Box, Tabs, Tab } from "@mui/material";
import FacilitiesForm from './tabs/FacilitiesForm';
import PathwaysForm from './tabs/PathwaysForm';
import ResourcesForm from './tabs/ResourcesForm';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import RouteIcon from '@mui/icons-material/Route';
import VaccinesIcon from '@mui/icons-material/Vaccines';
import TuneIcon from '@mui/icons-material/Tune';
import ConfigForm from './tabs/ConfigForm';





export default function DataGridForm({ activeTab, setActiveTab }) {
    const handleTabChange = (_, val) => {
        setActiveTab(val);
    };
    return (
        <Grid container sx={{ height: "50%", flexGrow: 1, alignItems: "right", minWidth: 0, width: "95%", mt: 10 }}>
            <Box sx={{ flexGrow: 1, minWidth: 0, width: "100%", ml: 5 }}>
                <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto" allowScrollButtonsMobile>
                    <Tab label="Facilities" value="tab-facilities" sx={{ fontSize: 10 }} icon={<LocalHospitalIcon sx={{ fontSize: 20 }} />} />
                    <Tab label="Pathways" value="tab-pathways" sx={{ fontSize: 10 }} icon={<RouteIcon sx={{ fontSize: 20 }} />} />
                    <Tab label="Resources" value="tab-resources" sx={{ fontSize: 10 }} icon={<VaccinesIcon sx={{ fontSize: 20 }} />} />
                    <Tab label="Model Configuration" value="tab-instance" sx={{ fontSize: 10, maxWidth: 80 }} icon={<TuneIcon sx={{ fontSize: 20 }} />} wrapped />
                </Tabs>
            </Box>
            {activeTab == "tab-facilities" && <FacilitiesForm />}
            {activeTab == "tab-pathways" && <PathwaysForm />}
            {activeTab == "tab-resources" && <ResourcesForm />}
            {activeTab == "tab-instance" && <ConfigForm />}
        </Grid >
    );
}

