import { AdminSideShell } from "../shells/admin-side-shell";
import { PageHeader } from "../compositions/page-header";
import { FilterBar } from "../compositions/filter-bar";
import { ActionBar } from "../compositions/action-bar";
import { Button } from "../primitives/button";
import { SelectField } from "../primitives/select-field";
import { DateField } from "../primitives/date-field";
import { StatusTag } from "../primitives/status-tag";
import { DataTable, type DataTableColumn, type DataTableRow } from "../primitives/data-table";
import { Panel } from "../primitives/panel";

type TaskRow = DataTableRow & {
  name: string;
  status: string;
  owner: string;
  updatedAt: string;
};

const columns: DataTableColumn<TaskRow>[] = [
  { title: "任务名称", dataIndex: "name", key: "name" },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    render: (value) => {
      const text = String(value);
      const tone =
        text === "进行中" ? "info" : text === "已完成" ? "success" : "warning";
      return <StatusTag tone={tone}>{text}</StatusTag>;
    },
  },
  { title: "负责人", dataIndex: "owner", key: "owner" },
  { title: "更新时间", dataIndex: "updatedAt", key: "updatedAt" },
];

const rows: TaskRow[] = [
  {
    key: "1",
    name: "企业认证资料复核",
    status: "进行中",
    owner: "张敏",
    updatedAt: "今天 10:24",
  },
  {
    key: "2",
    name: "开票信息变更审核",
    status: "待确认",
    owner: "李原",
    updatedAt: "今天 09:12",
  },
  {
    key: "3",
    name: "合同归档同步",
    status: "已完成",
    owner: "王哲",
    updatedAt: "昨天 18:05",
  },
];

export function ListManagementPage() {
  return (
    <AdminSideShell
      title="XFT 工作台"
      selectedKey="tasks"
      menuItems={[
        { key: "dashboard", label: "概览" },
        { key: "tasks", label: "任务管理" },
        { key: "settings", label: "设置" },
      ]}
      topExtra={<Button>帮助</Button>}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "var(--space-6)",
        }}
      >
        <PageHeader
          title="任务管理"
          description="用于查询、跟进与处理当前业务任务。"
          actions={<Button variant="primary">新建任务</Button>}
        />

        <FilterBar
          fields={[
            <SelectField
              key="status"
              placeholder="任务状态"
              options={[
                { label: "进行中", value: "processing" },
                { label: "待确认", value: "pending" },
                { label: "已完成", value: "done" },
              ]}
            />,
            <SelectField
              key="owner"
              placeholder="负责人"
              options={[
                { label: "张敏", value: "zhang" },
                { label: "李原", value: "li" },
                { label: "王哲", value: "wang" },
              ]}
            />,
            <DateField key="date" aria-label="日期筛选" />,
          ]}
          actions={
            <div style={{ display: "flex", gap: "var(--space-2)" }}>
              <Button>重置</Button>
              <Button variant="primary">查询</Button>
            </div>
          }
        />

        <ActionBar
          primary={<Button variant="primary">批量处理</Button>}
          secondary={[<Button key="export">导出</Button>]}
          tools={[<Button key="columns" variant="text">列设置</Button>]}
        />

        <Panel title="任务列表">
          <DataTable columns={columns} rows={rows} />
        </Panel>
      </div>
    </AdminSideShell>
  );
}
