import type { ReactNode } from "react";
import { Panel } from "../../primitives/panel";

export type DetailItem = {
  label: string;
  value: ReactNode;
};

export type DetailSectionBlock = {
  title?: string;
  items: DetailItem[];
};

export type DetailSectionProps = {
  title?: string;
  description?: string;
  items?: DetailItem[];
  sections?: DetailSectionBlock[];
};

export function DetailSection({
  title,
  description,
  items = [],
  sections = [],
}: DetailSectionProps) {
  const blocks = sections.length > 0 ? sections : [{ title: undefined, items }];

  return (
    <Panel title={title}>
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        {description ? (
          <p style={{ margin: 0, color: "var(--text-tertiary)" }}>{description}</p>
        ) : null}
        {blocks.map((block, index) => (
          <div
            key={block.title ?? `section-${index}`}
            style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}
          >
            {block.title ? (
              <h4
                style={{
                  margin: 0,
                  color: "var(--text-primary)",
                  fontSize: "var(--text-sm)",
                  fontWeight: "var(--weight-bold)",
                }}
              >
                {block.title}
              </h4>
            ) : null}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                gap: "var(--space-4) var(--space-6)",
              }}
            >
              {block.items.map((item) => (
                <div
                  key={item.label}
                  style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}
                >
                  <span style={{ color: "var(--text-tertiary)", fontSize: "var(--text-xs)" }}>
                    {item.label}
                  </span>
                  <span style={{ color: "var(--text-primary)" }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
