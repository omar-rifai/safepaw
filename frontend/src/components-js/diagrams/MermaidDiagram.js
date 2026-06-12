import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false });

export default function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  const id = useRef(`mmd-${Math.random().toString(36).slice(2)}`);
  const renderId = useRef(0);

  useEffect(() => {
    if (!chart || !ref.current) return;

    const current = ++renderId.current;

    const run = async () => {
      try {
        const { svg } = await mermaid.render(id.current, chart);

        if (current !== renderId.current) return;
        if (ref.current) ref.current.innerHTML = svg;
      } catch (e) {
        console.error("Mermaid render error:", e);
        if (ref.current) {
          ref.current.innerHTML = `<pre style="color:red">${e?.message || e}</pre>`;
        }
      }
    };

    run();
  }, [chart]);

  return <div ref={ref} />;
}