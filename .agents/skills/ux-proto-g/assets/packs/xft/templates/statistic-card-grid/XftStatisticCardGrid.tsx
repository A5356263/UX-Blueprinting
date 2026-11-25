import React, { ReactNode } from "react";
import "./XftStatisticCardGrid.css";
export type XftStatisticCardItem = { key: string; label: ReactNode; value: ReactNode; active?: boolean; onClick?: () => void };
export type XftStatisticCardGridMode = "interactive" | "summary";
export type XftStatisticCardGridProps = { items: XftStatisticCardItem[]; mode?: XftStatisticCardGridMode };
export function XftStatisticCardGrid({ items, mode = "interactive" }: XftStatisticCardGridProps) {
  const summary = mode === "summary";
  return <section className={`xft-statistic-card-grid xft-statistic-card-grid--${mode}`} aria-label="统计卡片区">
    {items.map((item) => {
      const interactive = !summary && Boolean(item.onClick);
      const activate = () => item.onClick?.();
      const className = `xft-statistic-card-grid__item${!summary && item.active ? " is-active" : ""}`;
      if (summary) {
        return <div key={item.key} className={className}><span>{item.label}</span><strong>{item.value}</strong></div>;
      }
      return <button key={item.key} type="button" className={className} onClick={interactive ? activate : undefined} disabled={!interactive} aria-pressed={interactive ? item.active : undefined}>
        <span>{item.label}</span><strong>{item.value}</strong>
      </button>;
    })}
  </section>;
}
