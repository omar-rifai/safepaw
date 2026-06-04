
import { DataContext } from '../../App';
import { useContext } from "react";
import { Stack} from '@mui/system';
import CaseMixDiagram from './CaseMixDiagram';



export default function ConfigChart() {
    const { inputData } = useContext(DataContext);

    const casemix = inputData?.instance_data?.case_mix ?? [];

    return (
         <Stack container spacing={1}>
            
            <CaseMixDiagram casemix={casemix}></CaseMixDiagram>
        </Stack>
    );
}