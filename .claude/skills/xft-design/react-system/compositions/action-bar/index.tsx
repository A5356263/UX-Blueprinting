import type { ReactNode } from "react";
import { Panel } from "../../primitives/panel";

export type ActionBarProps = {
  primary?: ReactNode;
  secondary?: ReactNode[];
  tools?: ReactNode[];
};

export function ActionBar({ primary, secondary = [], tools = [] }: ActionBarProps) {
  return (
    <Panel>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "var(--space-4)",
        }}
      >
        <div style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
          {primary}
          {secondary}
        </div>
        <div style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
          {tools}
        </div>
      </div>
    </Panel>
  );
}
