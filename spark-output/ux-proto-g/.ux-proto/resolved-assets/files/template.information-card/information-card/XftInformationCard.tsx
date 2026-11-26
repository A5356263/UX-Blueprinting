import React, { ReactNode } from "react";
import { Button, Dropdown } from "antd";
import { MoreOutlined } from "@ant-design/icons";
import "./XftInformationCard.css";
export type XftInformationCardDetail = { key: string; label: ReactNode; value: ReactNode };
export type XftInformationCardAction = { key: string; label: ReactNode; disabled?: boolean; onClick?: () => void };
export type XftInformationCardProps = {
  variant?: "detail-actions" | "icon-details-actions"; title: ReactNode; description?: ReactNode; icon?: ReactNode; tags?: ReactNode[];
  details?: XftInformationCardDetail[]; actions?: XftInformationCardAction[]; extra?: ReactNode;
  /** Enables the small elevation hover affordance. It is disabled by default. */
  interactive?: boolean;
  /** Applies the selected primary-color border. It is disabled by default. */
  selected?: boolean;
};
export function XftInformationCard({ variant = "detail-actions", title, description, icon, tags, details, actions, extra, interactive = false, selected = false }: XftInformationCardProps) {
  const detailItems = details ?? [];
  const actionItems = actions ?? [];
  const visibleActions = actionItems.slice(0, 3);
  const overflowActions = actionItems.slice(3);
  const iconVariant = variant === "icon-details-actions";
  return <article className={`xft-information-card xft-information-card--${variant}${interactive ? " xft-information-card--interactive" : ""}${selected ? " xft-information-card--selected" : ""}`}>
    <div className="xft-information-card__content">
      <div className="xft-information-card__heading">
        {iconVariant && icon ? <div className="xft-information-card__icon">{icon}</div> : null}
        <div className="xft-information-card__heading-main">
          <div className="xft-information-card__title-row"><h3>{title}</h3>{tags?.slice(0, 3).map((tag, index) => <React.Fragment key={index}>{tag}</React.Fragment>)}{extra ? <span className="xft-information-card__extra">{extra}</span> : null}</div>
          {description ? <p>{description}</p> : null}
        </div>
      </div>
      {detailItems.length ? <dl className="xft-information-card__details">{detailItems.map((detail) => <div key={detail.key}><dt>{detail.label}：</dt><dd>{detail.value}</dd></div>)}</dl> : null}
    </div>
    {actionItems.length ? <footer className="xft-information-card__actions" aria-label="卡片操作">
      {visibleActions.map((action) => <Button key={action.key} type="link" disabled={action.disabled} onClick={action.onClick}>{action.label}</Button>)}
      {overflowActions.length ? <Dropdown menu={{ items: overflowActions.map((action) => ({ key: action.key, label: action.label, disabled: action.disabled, onClick: action.onClick })) }}><Button className="xft-information-card__more" type="text" aria-label="更多操作" icon={<MoreOutlined />} /></Dropdown> : null}
    </footer> : null}
  </article>;
}
