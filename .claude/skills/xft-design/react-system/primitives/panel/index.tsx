import type { PropsWithChildren, ReactNode } from "react";

export type PanelProps = PropsWithChildren<{
  title?: ReactNode;
  extra?: ReactNode;
}>;

export function Panel({ title, extra, children }: PanelProps) {
  return (
    <section
      style={{
        background: "var(--card-bg)",
        border: "1px solid var(--border-default)",
        borderRadius: "var(--radius-lg)",
        boxShadow: "var(--shadow-subtle)",
        padding: "var(--space-6)",
      }}
    >
      {(title || extra) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "var(--space-4)",
          }}
        >
          {title ? (
            <h3
              style={{
                margin: 0,
                fontSize: "var(--text-h5)",
                fontWeight: "var(--weight-bold)",
                color: "var(--text-primary)",
              }}
            >
              {title}
            </h3>
          ) : (
            <span />
          )}
          {extra}
        </div>
      )}
      {children}
    </section>
  );
}
