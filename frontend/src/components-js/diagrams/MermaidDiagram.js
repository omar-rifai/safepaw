import { useEffect, useRef, useId } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false });

export default function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  const id = useId();

  useEffect(() => {
    if (!chart || !ref.current) return;
    let cancelled = false;
    const render = async () => {
      try {
        const { svg } = await mermaid.render(`mermaid-${id}`, chart);
        if (!cancelled && ref.current) {
          ref.current.innerHTML = svg;
        }
      } catch (e) {
        if (!cancelled && ref.current) {
          ref.current.innerHTML = `<pre style="color:red">${e.message}</pre>`;
        }
      }
    };

    render();
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  return <div ref={ref} />;
}