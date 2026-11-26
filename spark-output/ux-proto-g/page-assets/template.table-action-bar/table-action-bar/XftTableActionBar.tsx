// ux-proto-template: template.table-action-bar 79a7c765ff5b3824c56a018937059d939d2cb12b1639e7bfa6f027be95994611
import React, { type ReactNode } from "react";
import { Button, Dropdown, Space, Tooltip } from "antd";
import { ReloadOutlined, SettingOutlined, SortAscendingOutlined } from "@ant-design/icons";
import "./XftTableActionBar.css";

export type XftTableAction = {
  key: string;
  label: string;
  priority?: "primary" | "secondary" | "overflow";
  disabled?: boolean;
  danger?: boolean;
  onClick?: () => void;
};

export type XftTableActionBarProps = {
  actions?: XftTableAction[];
  onRefresh?: () => void;
  onSort?: () => void;
  onColumnSettings?: () => void;
  extraUtilities?: ReactNode;
  layout?: "split" | "right";
  section?: "all" | "actions" | "utilities";
};

export function XftTableActionBar({
  actions,
  onRefresh,
  onSort,
  onColumnSettings,
  extraUtilities,
  layout = "split",
  section = "all"
}: XftTableActionBarProps) {
  const items = actions ?? [];
  const ordinary = items.filter((item) => item.priority !== "overflow");
  const primary = ordinary.find((item) => item.priority === "primary");
  const ordered = primary ? [primary, ...ordinary.filter((item) => item !== primary)] : ordinary;
  const visible = ordered.slice(0, 5);
  const more = [...items.filter((item) => item.priority === "overflow"), ...ordered.slice(5)];
  const showActions = section !== "utilities";
  const showUtilities = section !== "actions";

  return <section className={"xft-table-action-bar xft-table-action-bar--" + layout + " xft-table-action-bar--" + section} role="toolbar" aria-label="页面内容操作栏">
    {showActions ? <Space className="xft-table-action-bar__business" size="small">
      {visible.map((item) => <Button key={item.key} type={item === primary ? "primary" : "default"} danger={item.danger} disabled={item.disabled} onClick={item.onClick}>{item.label}</Button>)}
      {more.length ? <Dropdown menu={{ items: more.map((item) => ({ key: item.key, label: item.label, danger: item.danger, disabled: item.disabled, onClick: item.onClick })) }}><Button>更多操作</Button></Dropdown> : null}
    </Space> : null}
    {showUtilities ? <Space className="xft-table-action-bar__utilities" size="small">
      <Tooltip title="刷新"><Button aria-label="刷新" icon={<ReloadOutlined />} disabled={!onRefresh} onClick={onRefresh} /></Tooltip>
      {onSort ? <Tooltip title="排序"><Button aria-label="排序" icon={<SortAscendingOutlined />} onClick={onSort} /></Tooltip> : null}
      <Tooltip title="表头设置"><Button aria-label="表头设置" icon={<SettingOutlined />} disabled={!onColumnSettings} onClick={onColumnSettings} /></Tooltip>
      {extraUtilities}
    </Space> : null}
  </section>;
}
