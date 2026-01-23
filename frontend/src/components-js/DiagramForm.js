import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend } from 'chart.js';
import { Chart } from 'react-chartjs-2';
import { useContext } from 'react';
import { DataContext, UIContext } from '../App';

// Register required Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend);

export default function ComposedChart() {
  const { outputData } = useContext(DataContext);
  const { deckGLData } = useContext(UIContext);

  const filtered_output = deckGLData.properties?.facility_id
    ? outputData.list_facility_load?.filter(
        (item) => item.properties.facility_id === deckGLData.properties?.facility_id
      )
    : outputData.list_facility_load;

  const facilities_data = filtered_output.map((f) => ({
    resource: f.properties.facility_id,
    capacity: f.properties?.capacities[0] - f.properties?.transfers_out[0],
    load: Math.round(f.properties?.load * 4.6),
    imported: f.properties?.transfers_in[0],
    exported: f.properties?.transfers_out[0],
  }));

  // Chart.js data structure
  const data = {
    labels: facilities_data.map(d => d.resource),
    datasets: [
      {
        type: 'bar',
        label: 'Capacity',
        data: facilities_data.map(d => d.capacity),
        backgroundColor: '#88adc8ff',
        stack: 'stack1',
        order:2
      },
      {
        type: 'bar',
        label: 'Imported',
        data: facilities_data.map(d => d.imported),
        backgroundColor: '#baecb4ff',
        stack: 'stack1',
        order:2
      },
      {
        type: 'bar',
        label: 'Exported',
        data: facilities_data.map(d => d.exported),
        backgroundColor: 'rgba(248,98,98,0.7)',
        stack: 'stack1',
        order:2
      },
      {
        type: 'line',
        label: 'Load',
        data: facilities_data.map(d => d.load),
        borderColor: '#0b6a8aff',
        spanGaps: true,
        borderWidth: 2,
        tension: 0.4,
        backgroundColor: 'transparent',
        pointRadius: 3,
        order:1
      },
    ],
  };

  // Chart.js options
  const options = {
    responsive: true,
    plugins: {
      tooltip: {
        mode: 'index',
        intersect: false,
      },
      legend: {
        position: 'bottom',
      },
    },
    scales: {
      x: {
        stacked: true,
        ticks: { display : false}
      },
      y: {
        stacked: true,
      },
    },
  };

  return <Chart type="bar" data={data} options={options} />;
}
