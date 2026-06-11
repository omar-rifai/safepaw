
import chroma from "chroma-js"
import { useMemo } from 'react';

const color_scale = chroma.scale(chroma.brewer.Set1)
function getColor(type) {
    if (!type) return [0, 0, 255, 100]
    const hash = [...type].reduce((a, c) => a + c.charCodeAt(0), 0);
    const [r, g, b, a] = color_scale(hash % 10 / 10).rgba();
    return [Math.round(r), Math.round(g), Math.round(b), Math.round(a * 200)];
}


export default function Legend({ inputData, outputData }) {


    const facilities = inputData?.facilities_capacities || [];

    const unique_types = useMemo(() => {
        return [...new Set(facilities.map(f => f.facility_type).filter(Boolean))];
    }, [facilities]);


    if (outputData && Object.keys(outputData).length !== 0) {

        return (<div style={{ position: 'absolute', bottom: 0, right: 0 }}>
            <div>± resources usage</div>
            <div style={{ width: 120, height: 20, background: 'linear-gradient(to right,rgba(0,0,255,0.1),rgba(255,0,0,0.7))' }}></div> </div>)
    }
    else if (inputData) {

        return (<div style={{ position: 'absolute', bottom: 20, right: 10, zIndex: 1 }}>
            {unique_types.length !== 0 && unique_types.map((type, i) => {
                const color = getColor(type);
                return (
                    <div key={type} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span
                            style={{
                                background: `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${color[3] / 255})`,
                                width: 20,
                                height: 20,
                                display: "inline-block"
                            }}
                        />
                        <span>{type ?? "unknown"}</span>
                    </div>
                );
            })}

        </div>);


    }
    return (<div></div>)

}
