import { useState, useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  applyNodeChanges,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes = [
  {
    id: '1',
    position: { x: 0, y: 0 },
    data: { label: 'Input Node' },
  },
  {
    id: '2',
    position: { x: 40, y: 80 },
    data: { label: 'Output Node' },
  },
];

const initialEdges = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
  },
];

export default function FlowDiagram() {
  const [nodes, setNodes] = useState(initialNodes);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={initialEdges}
        onNodesChange={onNodesChange}
        fitView
        fitViewOptions={{padding: 0, maxZoom: 1}}>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}