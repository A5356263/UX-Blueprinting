import type { ReactNode } from "react";

export type XftTableRow = Record<string, unknown> & {
  key: string;
};

export type XftTableColumn<Row extends XftTableRow> = {
  key: string;
  title: ReactNode;
  dataIndex: keyof Row;
  render?: (value: Row[keyof Row], row: Row) => ReactNode;
};

export type XftTableProps<Row extends XftTableRow> = {
  columns: XftTableColumn<Row>[];
  rows: Row[];
  emptyText?: string;
};

export function XftTable<Row extends XftTableRow>({
  columns,
  rows,
  emptyText = "暂无数据",
}: XftTableProps<Row>) {
  return (
    <div className="xft-table-wrap">
      <table className="xft-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? (
            rows.map((row) => (
              <tr key={row.key}>
                {columns.map((column) => {
                  const value = row[column.dataIndex];
                  return (
                    <td key={column.key}>
                      {column.render ? column.render(value, row) : String(value ?? "")}
                    </td>
                  );
                })}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} className="xft-table__empty">
                {emptyText}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
