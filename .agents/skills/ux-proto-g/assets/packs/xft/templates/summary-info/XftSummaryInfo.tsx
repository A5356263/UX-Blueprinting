import React, { ReactNode, useState } from "react";
import { Button, Divider, Dropdown, Space, Tooltip } from "antd";
import { DownOutlined, UpOutlined } from "@ant-design/icons";
import "./XftSummaryInfo.css";

export type XftSummaryInfoVariant = "custom" | "person" | "range";
export type XftSummaryInfoField = { key: string; label: ReactNode; value: ReactNode };
export type XftSummaryInfoStatistic = { key: string; label: ReactNode; value: ReactNode };
export type XftSummaryInfoRangeOption = { key: string; label: ReactNode };
export type XftSummaryInfoAction = { key: string; label: string; onClick?: () => void; disabled?: boolean };
export type XftSummaryInfoProps = {
  variant?: XftSummaryInfoVariant;
  title: ReactNode;
  showTitle?: boolean;
  avatar?: ReactNode;
  timeNote?: ReactNode;
  description?: ReactNode;
  tags?: ReactNode[];
  actions?: XftSummaryInfoAction[];
  fields?: XftSummaryInfoField[];
  statisticItems?: XftSummaryInfoStatistic[];
  statistics?: ReactNode;
  statisticsAction?: XftSummaryInfoAction;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  onTitleClick?: () => void;
  rangeOptions?: XftSummaryInfoRangeOption[];
  activeRangeKey?: string;
  onRangeChange?: (key: string) => void;
};

export function XftSummaryInfo({ variant = "custom", title, showTitle = true, avatar, timeNote, description, tags, actions, fields, statisticItems, statistics, statisticsAction, collapsible = false, defaultExpanded = true, onExpandedChange, onTitleClick, rangeOptions, activeRangeKey, onRangeChange }: XftSummaryInfoProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [rangeOpen, setRangeOpen] = useState(false);
  const [innerRangeKey, setInnerRangeKey] = useState<string | undefined>(activeRangeKey);
  const hasStatistics = Boolean(statisticItems?.length || statistics);
  const hasDetails = Boolean(fields?.length || hasStatistics);
  const canCollapse = collapsible && hasDetails;
  const visibleDetails = !canCollapse || expanded;
  const toggleExpanded = () => { const next = !expanded; setExpanded(next); onExpandedChange?.(next); };
  const chooseRange = (key: string) => { setInnerRangeKey(key); setRangeOpen(false); onRangeChange?.(key); };
  const rangeTrigger = <Button type="text" className="xft-list-page-header__range-trigger">{title}<DownOutlined /></Button>;
  const titleContent = variant === "range" && rangeOptions?.length ? <Dropdown open={rangeOpen} trigger={["click"]} onOpenChange={(open) => { setRangeOpen(open); if (open) onTitleClick?.(); }} dropdownRender={() => <div className="xft-list-page-header__range-picker-panel">{rangeOptions.map((option) => <Button key={option.key} type="text" className={`xft-list-page-header__range-option ${(activeRangeKey ?? innerRangeKey) === option.key ? "is-active" : ""}`} onClick={() => chooseRange(option.key)}>{option.label}</Button>)}</div>}>{rangeTrigger}</Dropdown> : variant === "range" ? <Button type="text" className="xft-list-page-header__range-trigger" onClick={onTitleClick}>{title}<DownOutlined /></Button> : <h1>{title}</h1>;
  const titleRow = <div className="xft-list-page-header__title-row">{showTitle ? <div className="xft-list-page-header__title">{titleContent}</div> : null}{timeNote ? <span className="xft-list-page-header__time">{timeNote}</span> : null}{tags?.slice(0, 3).map((tag, index) => <span className="xft-list-page-header__tag" key={index}>{tag}</span>)}{canCollapse ? <Button type="link" className="xft-list-page-header__collapse" icon={expanded ? <UpOutlined /> : <DownOutlined />} iconPosition="end" onClick={toggleExpanded}>{expanded ? "收起" : "展开"}</Button> : null}</div>;
  return <section className={`xft-list-page-header xft-list-page-header--${variant}${visibleDetails && fields?.length ? " xft-list-page-header--has-fields" : ""}`}><div className="xft-list-page-header__top">{variant === "person" && avatar ? <div className="xft-list-page-header__person"><span className="xft-list-page-header__avatar">{avatar}</span><div className="xft-list-page-header__person-content">{titleRow}{description ? <Tooltip title={description}><p className="xft-list-page-header__description">{description}</p></Tooltip> : null}</div></div> : <div>{titleRow}{description ? <Tooltip title={description}><p className="xft-list-page-header__description">{description}</p></Tooltip> : null}</div>}{actions?.length ? <Space className="xft-list-page-header__actions" size={16}>{actions.slice(0, 3).map((action) => <Button key={action.key} type="link" disabled={action.disabled} onClick={action.onClick}>{action.label}</Button>)}</Space> : null}</div>{visibleDetails && fields?.length ? <div className="xft-list-page-header__fields">{fields.slice(0, 4).map((field) => <div className="xft-list-page-header__field" key={field.key}><span>{field.label}</span><strong>{field.value}</strong></div>)}</div> : null}{visibleDetails && fields?.length && hasStatistics ? <Divider className="xft-list-page-header__divider" /> : null}{visibleDetails && hasStatistics ? <div className="xft-list-page-header__statistics">{statisticItems?.length ? <div className="xft-list-page-header__statistic-items">{statisticItems.map((item) => <div className="xft-list-page-header__statistic-item" key={item.key}><span>{item.label}</span><strong>{item.value}</strong></div>)}</div> : statistics}{statisticsAction ? <span className="xft-list-page-header__statistics-action"><Button type="link" disabled={statisticsAction.disabled} onClick={statisticsAction.onClick}>{statisticsAction.label}</Button></span> : null}</div> : null}</section>;
}
