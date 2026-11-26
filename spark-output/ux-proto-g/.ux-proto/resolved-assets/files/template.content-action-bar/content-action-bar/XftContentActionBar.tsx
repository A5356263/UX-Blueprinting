import { type ReactNode } from "react";
import "./XftContentActionBar.css";

export type XftContentActionBarSummaryItem = { key: string; label: ReactNode; value: ReactNode; unit?: string };
export type XftContentActionBarProps = {
  children?: ReactNode;
  summary?: XftContentActionBarSummaryItem[];
  layout?: "inline" | "stacked";
  ariaLabel?: string;
  align?: "start" | "center" | "end";
  embedded?: boolean;
};

export function XftContentActionBar({ children, summary, layout = "inline", ariaLabel = "内容操作", align = "center", embedded = false }: XftContentActionBarProps) {
  const hasSummary = Boolean(summary?.length);
  const hasActions = children !== undefined && children !== null;
  if (!hasSummary && !hasActions) return null;
  const className = ["xft-content-action-bar", hasSummary ? "xft-content-action-bar--with-summary" : "", layout === "stacked" ? "xft-content-action-bar--stacked" : "", embedded ? "xft-content-action-bar--embedded" : ""].filter(Boolean).join(" ");
  return <footer className={className} data-align={align} role="toolbar" aria-label={ariaLabel}>
    <div className="xft-content-action-bar__inner">
      {hasSummary ? <div className="xft-content-action-bar__summary">{summary!.map((item) => <span key={item.key} className="xft-content-action-bar__summary-item"><span className="xft-content-action-bar__summary-label">{item.label}</span><span className="xft-content-action-bar__summary-value">{item.value}{item.unit ? <span className="xft-content-action-bar__summary-unit">{item.unit}</span> : null}</span></span>)}</div> : null}
      {hasActions ? <div className="xft-content-action-bar__actions">{children}</div> : null}
    </div>
  </footer>;
}
