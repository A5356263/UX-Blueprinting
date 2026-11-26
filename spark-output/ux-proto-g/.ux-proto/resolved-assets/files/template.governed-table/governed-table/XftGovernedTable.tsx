import React, { ReactNode, useLayoutEffect, useRef, useState } from "react";
import { Badge, Button, Empty, Image, Input, Popover, Switch, Table, Tag, Tooltip } from "antd";
import type { TableColumnsType, TableProps } from "antd";
import { FilterFilled, QuestionCircleOutlined } from "@ant-design/icons";
import "./XftGovernedTable.css";

export type XftSemanticColor = "accent" | "info" | "success" | "warning" | "error";
export type XftTableColumn = { key: string; title: string; tooltip?: string; filterable?: boolean; filterKey?: string; field?: string; fields?: string[]; separator?: string; width?: number; align?: "left" | "center" | "right"; kind?: "text" | "tag" | "badge" | "link" | "switch" | "image"; color?: XftSemanticColor; onClick?: (record: Record<string, unknown>) => void; onChange?: (record: Record<string, unknown>, checked: boolean) => void; children?: XftTableColumn[]; sorter?: boolean | ((a: Record<string, unknown>, b: Record<string, unknown>) => number); sortOrder?: "ascend" | "descend" | null; renderCell?: (record: Record<string, unknown>) => ReactNode };
export type XftTableTextAction = { key: string; label: string; onClick: () => void; danger?: boolean; disabled?: boolean; disabledReason?: string };
export type XftGovernedTableProps = {
  columns: XftTableColumn[]; dataSource: Record<string, unknown>[]; rowKey?: string; rowSelection?: TableProps<Record<string, unknown>>["rowSelection"]; rowActions?: (record: Record<string, unknown>) => readonly XftTableTextAction[]; loading?: boolean; empty?: ReactNode; scrollOwner?: "table" | "page";
  filterValues?: Record<string, unknown>;
  renderColumnFilter?: (key: string, close: () => void) => ReactNode;
  headerVariant?: "default" | "finance-blue";
  rowClassName?: TableProps<Record<string, unknown>>["rowClassName"];
  onSortChange?: (key: string, order: "ascend" | "descend" | null) => void;
};

const getActionColumnWidth = (rows: readonly (readonly XftTableTextAction[])[]) => Math.max(72, ...rows.map((actions) => actions.reduce((width, action) => width + Math.max(2, Array.from(action.label).length) * 14, 32 + Math.max(0, actions.length - 1) * 16)));
const textOf = (value: unknown) => value === null || value === undefined ? "" : String(value);
const getColumnText = (column: XftTableColumn, record: Record<string, unknown>) => {
  const fields = column.fields?.length ? column.fields : column.field ? [column.field] : [];
  return fields.map((field) => textOf(record[field])).filter(Boolean).join(column.separator ?? " · ");
};

const XftSingleLineCell = ({ text, children }: { text: string; children: ReactNode }) => {
  const lineRef = useRef<HTMLSpanElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);
  useLayoutEffect(() => {
    const line = lineRef.current;
    if (!line) return;
    const checkOverflow = () => setIsOverflowing(line.scrollWidth > line.clientWidth || line.scrollHeight > line.clientHeight);
    checkOverflow();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(checkOverflow);
    observer.observe(line);
    return () => observer.disconnect();
  }, [text]);
  const content = <span ref={lineRef} className="xft-governed-table__cell-line">{children}</span>;
  return isOverflowing && text ? <Tooltip title={text}>{content}</Tooltip> : content;
};

const semanticColors: Record<XftSemanticColor, { color: string; backgroundColor: string }> = {
  accent: { color: "var(--alias-surface-accent-solid)", backgroundColor: "var(--alias-surface-accent-tint)" },
  info: { color: "var(--alias-surface-info-solid)", backgroundColor: "var(--alias-surface-info-tint)" },
  success: { color: "var(--alias-surface-success-solid)", backgroundColor: "var(--alias-surface-success-tint)" },
  warning: { color: "var(--alias-surface-warning-solid)", backgroundColor: "var(--alias-surface-warning-tint)" },
  error: { color: "var(--alias-surface-error-solid)", backgroundColor: "var(--alias-surface-error-tint)" }
};
const neutralTagColors = { color: "var(--alias-text-default)", backgroundColor: "var(--alias-surface-container-muted)" };
const neutralBadgeColor = "var(--alias-text-muted)";

const hasFilterValue = (value: unknown) => value !== null && value !== undefined && value !== "" && value !== false && (!Array.isArray(value) || value.some(Boolean));
const createDataColumns = (columns: XftTableColumn[], filterValues: Record<string, unknown>, renderColumnFilter: XftGovernedTableProps["renderColumnFilter"], openFilterKey: string | null, setOpenFilterKey: (key: string | null) => void): TableColumnsType<Record<string, unknown>> => columns.map((column) => {
  if (column.children?.length) return { key: column.key, title: column.title, children: createDataColumns(column.children, filterValues, renderColumnFilter, openFilterKey, setOpenFilterKey) };
  return {
  key: column.key,
  title: <span className="xft-governed-table__column-title"><span>{column.title}</span>{column.tooltip ? <Tooltip title={column.tooltip}><span className="xft-governed-table__column-tooltip" tabIndex={0} aria-label={column.tooltip}><QuestionCircleOutlined /></span></Tooltip> : null}{column.filterable && renderColumnFilter ? <Popover placement="bottomLeft" overlayClassName="xft-governed-table__filter-popover" trigger="click" destroyOnHidden open={openFilterKey === (column.filterKey ?? column.key)} onOpenChange={(open) => setOpenFilterKey(open ? column.filterKey ?? column.key : null)} content={renderColumnFilter(column.filterKey ?? column.key, () => setOpenFilterKey(null))}><button type="button" className={`xft-governed-table__filter-icon${hasFilterValue(filterValues[column.filterKey ?? column.key]) ? " is-active" : ""}`} aria-label={`筛选${column.title}`} aria-pressed={hasFilterValue(filterValues[column.filterKey ?? column.key])}><FilterFilled /></button></Popover> : null}</span>,
  width: column.width,
  align: column.align,
  className: column.sorter ? "xft-governed-table__sortable-column" : undefined,
  sorter: column.sorter,
  sortOrder: column.sortOrder,
  ...(column.field ? { dataIndex: column.field } : {}),
  render: (_value: unknown, record: Record<string, unknown>) => {
    if (column.renderCell) return column.renderCell(record);
    const text = getColumnText(column, record);
    const color = column.color ? semanticColors[column.color] : undefined;
    const visible = column.kind === "tag"
      ? <Tag style={color ?? neutralTagColors}>{text || "—"}</Tag>
      : column.kind === "badge"
        ? <Badge color={color?.color ?? neutralBadgeColor} text={text || "—"} />
        : column.kind === "link" && column.onClick
          ? <Button className="xft-governed-table__cell-link" type="link" onClick={() => column.onClick?.(record)}>{text || "—"}</Button>
          : column.kind === "switch" && column.field
            ? <Switch checked={Boolean(record[column.field])} aria-label={column.title} onChange={(checked) => column.onChange?.(record, checked)} />
            : column.kind === "image"
              ? text ? <Image className="xft-governed-table__cell-image" src={text} alt={column.title} width={72} height={32} preview={{ zIndex: 1400 }} /> : "—"
              : text || "—";
    return <XftSingleLineCell text={column.kind === "image" ? "" : text}>{visible}</XftSingleLineCell>;
  }
  };
});

export function XftGovernedTable({ columns, dataSource, rowKey = "key", rowSelection, rowActions, loading, empty, scrollOwner = "table", filterValues, renderColumnFilter, headerVariant = "default", rowClassName, onSortChange }: XftGovernedTableProps) {
  const [scrollContainer, setScrollContainer] = useState<HTMLDivElement | null>(null);
  const [openFilterKey, setOpenFilterKey] = useState<string | null>(null);
  const actionsByRow = rowActions ? dataSource.map((record) => ({ record, actions: rowActions(record) })) : [];
  const dataColumns = createDataColumns(columns, filterValues ?? {}, renderColumnFilter, openFilterKey, setOpenFilterKey);
  const actionColumn = rowActions ? { key: "__xft_row_actions__", title: "操作", fixed: "right" as const, width: getActionColumnWidth(actionsByRow.map(({ actions }) => actions)), render: (_value: unknown, record: Record<string, unknown>) => {
    const actions = actionsByRow.find((item) => item.record === record)?.actions ?? rowActions(record);
    return <div className="xft-governed-table__row-actions">{actions.map((action) => <Button key={action.key} type="link" danger={action.danger} disabled={action.disabled} title={action.disabledReason} aria-label={action.disabledReason ? `${action.label}：${action.disabledReason}` : action.label} onClick={action.onClick}>{action.label}</Button>)}</div>;
  } } : null;
  return <div ref={scrollOwner === "table" ? setScrollContainer : undefined} className={`xft-governed-table xft-governed-table--${scrollOwner} xft-governed-table--${headerVariant}`}><Table<Record<string, unknown>> rowKey={rowKey} rowSelection={rowSelection} sticky={scrollOwner === "table" && scrollContainer ? { getContainer: () => scrollContainer, offsetHeader: 0 } : false} scroll={{ x: "max-content" }} columns={actionColumn ? [...dataColumns, actionColumn] : dataColumns} dataSource={dataSource} loading={loading} rowClassName={rowClassName} onChange={onSortChange ? (_pagination, _filters, sorter) => { const active = Array.isArray(sorter) ? sorter[0] : sorter; onSortChange(String(active?.columnKey ?? ""), active?.order ?? null); } : undefined} pagination={false} locale={{ emptyText: empty ?? <Empty description="暂无数据" /> }} /></div>;
}

export type XftSchemeManagerTableProps = {
  schemes: readonly { id: string; name: string; isDefault?: boolean }[];
  onRename: (id: string, name: string) => void;
  onDefault: (id: string) => void;
  onDelete: (id: string) => void;
};

export function XftSchemeManagerTable({ schemes, onRename, onDefault, onDelete }: XftSchemeManagerTableProps) {
  const rows = schemes.map((scheme) => ({ key: scheme.id, scheme }));
  const columns: XftTableColumn[] = [
    { key: "name", title: "筛选方案名称", width: 232, renderCell: (record) => {
      const scheme = record.scheme as XftSchemeManagerTableProps["schemes"][number];
      return <Input aria-label={`方案名称：${scheme.name}`} value={scheme.name} maxLength={30} onChange={(event) => onRename(scheme.id, event.target.value)} />;
    } },
    { key: "default", title: "默认显示", width: 96, align: "center", renderCell: (record) => {
      const scheme = record.scheme as XftSchemeManagerTableProps["schemes"][number];
      return <label className="xft-scheme-manager-table__default"><input type="radio" name="xft-default-scheme" checked={Boolean(scheme.isDefault)} onChange={() => onDefault(scheme.id)} />默认</label>;
    } }
  ];
  return <div className="xft-scheme-manager-table"><XftGovernedTable scrollOwner="page" columns={columns} dataSource={rows} rowActions={(record) => [{ key: "delete", label: "删除", disabled: schemes.length <= 1, onClick: () => onDelete(String(record.key)) }]} /></div>;
}
