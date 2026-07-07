import { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  applyNodeChanges,
  ControlButton,
} from '@xyflow/react';
import {Dialog, DialogContent} from '@mui/material';
import '@xyflow/react/dist/style.css';
import { getInitialNodes, nodeTypes } from "./nodes"
import { getInitialEdges } from "./edges"



export default function FlowDiagram({ activities }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([])
  const [openDialog, setOpenDialog] = useState(false)

  function handleOpenDialog(){
    setOpenDialog(true)
  }

  function handleCloseDialog(){
    setOpenDialog(false)
  }

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  useEffect(() => {
    const new_nodes = getInitialNodes(activities)
    const new_edges = getInitialEdges(activities)
    setNodes(new_nodes)
    setEdges(new_edges)
  }, [activities])


  return (
      <div style={{ width: '500px', height: '300px', overflow: 'hidden', minHeight: 0, position: 'relative' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        nodeTypes={nodeTypes}

        panOnScroll={true}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.8}
        maxZoom={2}
        translateExtent={[[-1000, -1000], [2000, 2000]]}
        nodeExtent={[[-1000, -1000], [2000, 2000]]}
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls  style={{ position: 'absolute', bottom: 20, left: 10 }}>
          <ControlButton onClick={handleOpenDialog}> Add</ControlButton>
        </Controls>
      </ReactFlow>
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogContent>Not implemented</DialogContent>
      </Dialog>
    </div>
  );
}