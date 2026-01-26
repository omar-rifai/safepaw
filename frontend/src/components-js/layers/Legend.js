export default function Legend({ layers }) {
    if (layers[0]?.id == "facilities-volume") {
        return (<div style={{ position: 'absolute', bottom: 0, right: 0 }}>
            <div>± beds usage</div>
            <div style={{ width: 120, height: 20, background: 'linear-gradient(to right,rgba(0,0,255,0.1),rgba(255,0,0,0.7))' }}></div> </div>)
    }
    else if (layers[0]?.id == "facilities-capacity") {
        return (<div style={{ position: 'absolute', bottom: 0, right: 0, zIndex: 1 }}>
            <div><span style={{ background: 'rgba(173, 216, 230, 0.7)', width: 20, height: 20, display: 'inline-block' }} /> 1</div>
             <div><span style={{ background: 'rgba(100, 200, 150, 0.7)', width: 20, height: 20, display: 'inline-block' }} /> 2a</div>
            <div><span style={{ background: 'rgba(60, 160, 90, 0.7)', width: 20, height: 20, display: 'inline-block' }} /> 2b</div>
            <div><span style={{ background: 'rgba(0, 100, 0, 0.7)' , width: 20, height: 20, display: 'inline-block' }} /> 3</div> </div>);
    }

}
