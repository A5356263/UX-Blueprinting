import { Panel } from "../../primitives/panel";
import { StatusTag, type StatusTone } from "../../primitives/status-tag";

export type SummaryItem = {
  label: string;
  value: string;
  tone?: StatusTone;
};

export type SummaryStripProps = {
  items: SummaryItem[];
};

export function SummaryStrip({ items }: SummaryStripProps) {
  return (
    <Panel>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))`,
          gap: "var(--space-4)",
        }}
      >
        {items.map((item) => (
          <div
            key={item.label}
            style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}
          >
            <span style={{ color: "var(--text-tertiary)", fontSize: "var(--text-xs)" }}>
              {item.label}
            </span>
            <span
              style={{
                color: "var(--text-primary)",
                fontSize: "var(--text-h4)",
                fontWeight: "var(--weight-bold)",
              }}
            >
              {item.value}
            </span>
            {item.tone ? <StatusTag tone={item.tone}>{item.tone}</StatusTag> : null}
          </div>
        ))}
      </div>
    </Panel>
  );
}
