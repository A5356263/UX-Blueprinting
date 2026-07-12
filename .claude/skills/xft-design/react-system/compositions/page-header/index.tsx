import type { ReactNode } from "react";

export type PageHeaderProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <header
      style={{
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        gap: "var(--space-4)",
      }}
    >
      <div>
        <h1
          style={{
            margin: 0,
            fontSize: "var(--text-h3)",
            fontWeight: "var(--weight-bold)",
            color: "var(--text-primary)",
          }}
        >
          {title}
        </h1>
        {description ? (
          <p
            style={{
              margin: "var(--space-2) 0 0",
              color: "var(--text-tertiary)",
            }}
          >
            {description}
          </p>
        ) : null}
      </div>
      {actions}
    </header>
  );
}
