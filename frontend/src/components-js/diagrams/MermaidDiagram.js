import { useEffect, useRef, useId } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false });

export default function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  const id = useId();

  useEffect(() => {
    if (!chart || !ref.current) return;

    const render = async () => {
      try {
        const { svg } = await mermaid.render(`mermaid-${id}`, chart);
        ref.current.innerHTML = svg;
      } catch (e) {
        ref.current.innerHTML = `<pre style="color:red">${e.message}</pre>`;
      }
    };

    render();
  }, [chart, id]);

  return <div ref={ref} />;
}