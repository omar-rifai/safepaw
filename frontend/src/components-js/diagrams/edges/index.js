
  export function getInitialEdges(activities) {
    
    const initialEdges = activities.filter(a=>a.transferable==true).map((a, index)=> (
      {
        id: `e${a.id}-${a.transfer_to}`,
        source: a.id.toString(),
        target: a.transfer_to.toString(),
      } 
    ));

    return initialEdges
  }