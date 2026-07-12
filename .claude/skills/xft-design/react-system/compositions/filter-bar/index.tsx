import type { ReactNode } from "react";
import { Panel } from "../../primitives/panel";

export type FilterBarProps = {
  fields: ReactNode[];
  actions?: ReactNode;
};

export function FilterBar({ fields, actions }: FilterBarProps) {
  return (
    <Panel>
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "space-between",
          gap: "var(--space-4)",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "var(--space-4)",
            flexWrap: "wrap",
            flex: 1,
          }}
        >
          {fields}
        </div>
        {actions}
      </div>
    </Panel>
  );
}
