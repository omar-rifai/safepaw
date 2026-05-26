import { Typography, Card } from '@mui/material';
import { ResponsiveContainer, PieChart, Pie } from 'recharts';

export default function GaugeChart({ steps, activeIndex, stops, label= "" }) {

    const getColor = (value) => {
        const val = Math.max(0, Math.min(99, value)) / 100 * (stops.length - 1);
        const i = Math.floor(val);
        const t = val - i;
        const hex = (a, b) => Math.round(a + t * (b - a));
        const parse = h => [1, 3, 5].map(o => parseInt(h.slice(o, o + 2), 16));
        const [r, g, b] = parse(stops[i]).map((c, j) => hex(c, parse(stops[i + 1])[j]));
        return `#${[r, g, b].map(c => c.toString(16).padStart(2, '0')).join('')}`;
    };


    const meterData = Array.from({ length: steps }, (_, i) => ({
        name: `step-${i}`,
        value: 1,
        fill: getColor((i / (steps - 1)) * 100),
    }));


    const needleData = meterData.map(d => ({ ...d, fill: 'transparent' }));
    const NEEDLE_COLOR = '#02031ca2';

    const Needle = ({ cx, cy, midAngle, innerRadius, outerRadius }) => {
        const needleLength = innerRadius + (outerRadius - innerRadius) / 2;
        return (
            <g>
                <circle cx={cx} cy={cy} r={5} fill={NEEDLE_COLOR} stroke="none" />
                <path
                    d={`M${cx},${cy}l${needleLength},0`}
                    strokeWidth={2}
                    stroke={NEEDLE_COLOR}
                    fill={NEEDLE_COLOR}
                    style={{
                        transform: `rotate(-${midAngle}deg)`,
                        transformOrigin: `${cx}px ${cy}px`,
                    }}
                />
            </g>
        );
    };


    const sharedPieProps = {
        dataKey: "value",
        cx: "50%",
        cy: "50%",
        startAngle: 180,
        endAngle: 0,
        innerRadius: 65,
        outerRadius: 100,
    };

    return (

        <ResponsiveContainer width="220" height="220" >

            <Typography sx={{
                pl:"10%",
                fontFamily: "Roboto", fontWeight: 70,
                color: "#333333"
            }}> 
            {label}
            </Typography>
            <PieChart>
                {/* Layer 1: colored segments */}
                <Pie {...sharedPieProps} data={meterData} />

                {/* Layer 2: invisible, just for the needle */}
                <Pie
                    {...sharedPieProps}
                    data={needleData}
                    activeIndex={activeIndex}
                    shape={(props) => activeIndex === props.index ? <Needle {...props} /> : <g />}
                />s

            </PieChart>

        </ResponsiveContainer>

    );
}