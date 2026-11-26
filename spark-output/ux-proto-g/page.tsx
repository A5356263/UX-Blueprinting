import { useState } from "react";
import { App, Breadcrumb, Button, Checkbox, Modal, Space, Typography } from "antd";
import { XftApplicationFrame } from "./page-assets/template.application-frame/XftApplicationFrame";
import { XftFilterBar } from "./page-assets/template.filter-bar/filter-bar/XftFilterBar";
import { XftGovernedTable } from "./page-assets/template.governed-table/governed-table/XftGovernedTable";
import type { XftTableColumn } from "./page-assets/template.governed-table/governed-table/XftGovernedTable";
import { XftTableActionBar } from "./page-assets/template.table-action-bar/table-action-bar/XftTableActionBar";

type ScopeCategory = "org" | "feature";

type Subadmin = {
  key: string;
  name: string;
  phone: string;
  department: string;
  orgScope: string[];
  featureScope: string[];
};

type Employee = {
  key: string;
  name: string;
  phone: string;
  department: string;
  joined: boolean;
  verified: boolean;
  isSubadmin: boolean;
  orgScope: string[];
  featureScope: string[];
};

type CopyResult = {
  key: string;
  name: string;
  status: "已生效" | "未处理";
  reason?: string;
  orgScope: string[];
  featureScope: string[];
};

type FilterValues = {
  name: string;
  phone: string;
  department: string;
};

const emptyFilters: FilterValues = { name: "", phone: "", department: "" };

const initialSubadmins: Subadmin[] = [
  { key: "sa-1", name: "林知远", phone: "13800001001", department: "产品部", orgScope: ["华东区域", "华南区域"], featureScope: ["员工档案", "权限报表"] },
  { key: "sa-2", name: "周雨桐", phone: "13800001002", department: "人力资源部", orgScope: ["总部", "华东区域"], featureScope: ["员工档案"] },
  { key: "sa-3", name: "陈亦航", phone: "13800001003", department: "研发部", orgScope: ["研发中心"], featureScope: ["权限报表", "组织管理"] },
  { key: "sa-4", name: "许安宁", phone: "13800001004", department: "财务部", orgScope: ["总部"], featureScope: ["薪资代发"] },
];

const initialEmployees: Employee[] = [
  { key: "emp-1", name: "苏宁", phone: "13800002001", department: "产品部", joined: true, verified: true, isSubadmin: true, orgScope: ["总部"], featureScope: ["员工档案"] },
  { key: "emp-2", name: "唐明", phone: "13800002002", department: "研发部", joined: true, verified: true, isSubadmin: false, orgScope: [], featureScope: [] },
  { key: "emp-3", name: "顾晨曦", phone: "13800002003", department: "人力资源部", joined: true, verified: true, isSubadmin: false, orgScope: [], featureScope: [] },
  { key: "emp-4", name: "沈嘉禾", phone: "13800002004", department: "财务部", joined: true, verified: true, isSubadmin: true, orgScope: ["总部"], featureScope: ["薪资代发"] },
  { key: "emp-5", name: "叶清越", phone: "13800002005", department: "运营部", joined: true, verified: true, isSubadmin: false, orgScope: [], featureScope: [] },
  { key: "emp-6", name: "季闻舟", phone: "13800002006", department: "研发部", joined: true, verified: true, isSubadmin: false, orgScope: [], featureScope: [] },
];

const filterFields = [
  { key: "name", label: "姓名", placeholder: "请输入姓名" },
  { key: "phone", label: "手机号", placeholder: "请输入手机号" },
  {
    key: "department",
    label: "部门",
    type: "select" as const,
    placeholder: "全部部门",
    options: [
      { label: "全部部门", value: "" },
      { label: "产品部", value: "产品部" },
      { label: "人力资源部", value: "人力资源部" },
      { label: "研发部", value: "研发部" },
      { label: "财务部", value: "财务部" },
      { label: "运营部", value: "运营部" },
    ],
  },
];

function unionScopes(current: string[], incoming: string[]) {
  return Array.from(new Set([...current, ...incoming]));
}

function formatScope(scope: string[]) {
  return scope.length ? scope.join("、") : "—";
}

export default function Page() {
  const { message } = App.useApp();
  const [subadmins, setSubadmins] = useState(initialSubadmins);
  const [employees, setEmployees] = useState(initialEmployees);
  const [filters, setFilters] = useState<FilterValues>(emptyFilters);
  const [appliedFilters, setAppliedFilters] = useState<FilterValues>(emptyFilters);
  const [source, setSource] = useState<Subadmin | null>(null);
  const [copyOpen, setCopyOpen] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [categories, setCategories] = useState<ScopeCategory[]>(["org", "feature"]);
  const [selectedEmployeeKeys, setSelectedEmployeeKeys] = useState<string[]>([]);
  const [stagedEmployeeKeys, setStagedEmployeeKeys] = useState<Set<string>>(new Set());
  const [categoryError, setCategoryError] = useState("");
  const [targetError, setTargetError] = useState("");
  const [targetFailures, setTargetFailures] = useState<CopyResult[]>([]);
  const [copyResults, setCopyResults] = useState<CopyResult[] | null>(null);

  const visibleSubadmins = subadmins.filter((item) =>
    item.name.includes(appliedFilters.name.trim()) &&
    item.phone.includes(appliedFilters.phone.trim()) &&
    (!appliedFilters.department || item.department === appliedFilters.department),
  );

  const columns: XftTableColumn[] = [
    { key: "name", title: "姓名", field: "name", width: 120 },
    { key: "phone", title: "手机号", field: "phone", width: 150 },
    { key: "department", title: "部门", field: "department", width: 150 },
    {
      key: "orgScope",
      title: "可授权组织",
      field: "orgScope",
      renderCell: (record) => <span className="scope-cell">{formatScope(record.orgScope as string[])}</span>,
    },
    {
      key: "featureScope",
      title: "可授权功能",
      field: "featureScope",
      renderCell: (record) => <span className="scope-cell">{formatScope(record.featureScope as string[])}</span>,
    },
  ];

  const selectedEmployees = selectedEmployeeKeys
    .map((key) => employees.find((employee) => employee.key === key))
    .filter((employee): employee is Employee => Boolean(employee));

  const eligibleEmployees = employees.filter((employee) => employee.joined && employee.verified);

  function resetCopyState() {
    setCopyOpen(false);
    setPickerOpen(false);
    setSource(null);
    setCategories(["org", "feature"]);
    setSelectedEmployeeKeys([]);
    setStagedEmployeeKeys(new Set());
    setCategoryError("");
    setTargetError("");
    setTargetFailures([]);
    setCopyResults(null);
  }

  function beginCopy(row: Subadmin) {
    setSource(row);
    setCategories(["org", "feature"]);
    setSelectedEmployeeKeys([]);
    setCategoryError("");
    setTargetError("");
    setTargetFailures([]);
    setCopyResults(null);
    setCopyOpen(true);
  }

  function openEmployeePicker() {
    setStagedEmployeeKeys(new Set(selectedEmployeeKeys));
    setPickerOpen(true);
  }

  function toggleCategory(category: ScopeCategory, checked: boolean) {
    setCategories((current) => checked
      ? Array.from(new Set([...current, category]))
      : current.filter((item) => item !== category));
    setCategoryError("");
  }

  function submitCopy() {
    if (!categories.length) {
      setCategoryError("请选择复制信息");
      return;
    }
    if (!selectedEmployeeKeys.length) {
      setTargetError("请选择至少一名复制对象");
      return;
    }
    if (!source) return;

    const selected = selectedEmployeeKeys
      .map((key) => employees.find((employee) => employee.key === key))
      .filter((employee): employee is Employee => Boolean(employee));
    const failures: CopyResult[] = [];
    const valid: Employee[] = [];

    selected.forEach((employee) => {
      if (!employee.joined) {
        failures.push({ key: employee.key, name: employee.name, status: "未处理", reason: "加入状态不是已加入，不能成为子管理员", orgScope: employee.orgScope, featureScope: employee.featureScope });
      } else if (!employee.verified) {
        failures.push({ key: employee.key, name: employee.name, status: "未处理", reason: "未完成实名认证，不能成为子管理员", orgScope: employee.orgScope, featureScope: employee.featureScope });
      } else {
        valid.push(employee);
      }
    });

    setTargetFailures(failures);
    setTargetError("");
    if (!valid.length) {
      if (!failures.length) setTargetError("所选员工信息已变化，请重新选择");
      return;
    }

    const results: CopyResult[] = valid.map((employee) => {
      const orgScope = employee.isSubadmin
        ? categories.includes("org") ? unionScopes(employee.orgScope, source.orgScope) : employee.orgScope
        : source.orgScope;
      const featureScope = employee.isSubadmin
        ? categories.includes("feature") ? unionScopes(employee.featureScope, source.featureScope) : employee.featureScope
        : source.featureScope;
      return { key: employee.key, name: employee.name, status: "已生效", orgScope, featureScope };
    });

    setEmployees((current) => current.map((employee) => {
      const result = results.find((item) => item.key === employee.key);
      return result ? { ...employee, isSubadmin: true, orgScope: result.orgScope, featureScope: result.featureScope } : employee;
    }));
    setSubadmins((current) => {
      const updated = results.map((result) => {
        const employee = employees.find((item) => item.key === result.key)!;
        return {
          key: employee.key,
          name: employee.name,
          phone: employee.phone,
          department: employee.department,
          orgScope: result.orgScope,
          featureScope: result.featureScope,
        };
      });
      const updatedKeys = new Set(updated.map((item) => item.key));
      return [...current.filter((item) => !updatedKeys.has(item.key)), ...updated];
    });
    setCopyResults([...results, ...failures]);
    message.success("复制成功");
  }

  const frameTabs = {
    tabs: [{ key: "permission-mode", label: "权限管理模式", closable: false }],
    activeKey: "permission-mode",
    onActivate: () => undefined,
    onClose: () => undefined,
    onNavigate: () => undefined,
    onCloseAll: () => undefined,
  };

  return (
    <XftApplicationFrame
      sideNavigationItems={[{ key: "permission", label: "通用权限管理" }]}
      activeSideNavigationKey="permission"
      workspaceTabBar={frameTabs}
    >
      <main className="subadmin-page" data-xft-scroll-owner="template">
        <Breadcrumb items={[
          { title: "管理后台" },
          { title: "通用权限管理" },
          { title: "权限管理模式" },
          { title: "子管理员模式" },
        ]} />

        <div className="mode-tabs" role="tablist" aria-label="权限管理模式">
          <button className="mode-tab active" role="tab" aria-selected="true" type="button">子管理员模式</button>
          <button className="mode-tab" role="tab" aria-selected="false" type="button" onClick={() => message.info("双管理员互审模式当前未启用")}>双管理员互审模式 <span className="mode-state">未启用</span></button>
          <button className="mode-tab" role="tab" aria-selected="false" type="button" onClick={() => message.info("权限变更审批模式当前未启用")}>权限变更审批模式 <span className="mode-state">未启用</span></button>
        </div>

        <section className="intro-row" aria-label="模式说明">
          <Typography.Text type="secondary">管理子管理员可授权的组织与功能范围。</Typography.Text>
          <Space size={12}>
            <Button type="link" onClick={() => message.info("帮助文档入口")}>帮助文档</Button>
            <Button onClick={() => message.info("此入口沿用现有的关闭子管理员模式流程")}>关闭子管理员模式</Button>
          </Space>
        </section>

        <XftFilterBar
          fields={filterFields}
          value={filters}
          defaultValue={emptyFilters}
          onChange={setFilters}
          onQuery={(value) => setAppliedFilters(value as FilterValues)}
          onReset={(value) => setAppliedFilters(value as FilterValues)}
        />

        <XftTableActionBar
          section="actions"
          actions={[{
            key: "add-subadmin",
            label: "添加子管理员",
            onClick: () => message.info("此入口沿用现有的添加子管理员流程"),
          }]}
        />

        <div className="table-region">
          <XftGovernedTable
            columns={columns}
            dataSource={visibleSubadmins}
            rowKey="key"
            empty="暂无内容"
            rowActions={(record) => {
              const row = subadmins.find((item) => item.key === String(record.key));
              if (!row) return [];
              return [
                { key: "copy", label: "复制", onClick: () => beginCopy(row) },
                { key: "edit", label: "编辑", onClick: () => message.info("此入口沿用现有编辑流程") },
                { key: "remove", label: "移除", onClick: () => message.info("此入口沿用现有移除流程") },
              ];
            }}
          />
        </div>
      </main>

      <Modal
        className="copy-modal"
        title="复制"
        open={copyOpen}
        width={680}
        footer={null}
        onCancel={resetCopyState}
        destroyOnHidden
      >
        {copyResults ? (
          <div className="copy-result-view">
            <Typography.Title level={5}>本次处理结果</Typography.Title>
            <div className="result-list">
              {copyResults.map((result) => (
                <div className="result-item" key={result.key}>
                  <div className="result-heading">
                    <Typography.Text strong>{result.name}</Typography.Text>
                    <span className={`result-status ${result.status === "已生效" ? "is-success" : "is-pending"}`}>{result.status}</span>
                  </div>
                  {result.reason ? (
                    <Typography.Text type="secondary">未处理原因：{result.reason}</Typography.Text>
                  ) : (
                    <div className="result-scopes">
                      <Typography.Text type="secondary">可授权组织：{formatScope(result.orgScope)}</Typography.Text>
                      <Typography.Text type="secondary">可授权功能：{formatScope(result.featureScope)}</Typography.Text>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="modal-footer">
              <Button type="primary" onClick={resetCopyState}>完成</Button>
            </div>
          </div>
        ) : (
          <>
            <div className="copy-source">
              <Typography.Text type="secondary">复制来源：</Typography.Text>
              <Typography.Text>{source ? `${source.name} / ${source.phone}` : "—"}</Typography.Text>
            </div>

            <section className="copy-section">
              <Typography.Text strong>复制信息</Typography.Text>
              <div className="category-options">
                <Checkbox checked={categories.includes("org")} onChange={(event) => toggleCategory("org", event.target.checked)}>可授权组织</Checkbox>
                <Checkbox checked={categories.includes("feature")} onChange={(event) => toggleCategory("feature", event.target.checked)}>可授权功能</Checkbox>
              </div>
              <Typography.Text type="secondary">至少选择一项</Typography.Text>
              {categoryError && <div className="inline-error" role="alert">{categoryError}</div>}
            </section>

            <section className="copy-section target-section">
              <div className="section-heading">
                <Typography.Text strong>复制对象</Typography.Text>
                <Button onClick={openEmployeePicker}>选择员工</Button>
              </div>
              {selectedEmployees.length ? (
                <div className="selected-employee-list">
                  {selectedEmployees.map((employee) => (
                    <div className="selected-employee" key={employee.key}>
                      <span>{employee.name} <Typography.Text type="secondary">{employee.phone}</Typography.Text></span>
                      <Button type="link" size="small" onClick={() => {
                        setSelectedEmployeeKeys((current) => current.filter((key) => key !== employee.key));
                        setTargetFailures([]);
                        setTargetError("");
                      }}>移除</Button>
                    </div>
                  ))}
                </div>
              ) : <div className="empty-selection">暂未选择员工</div>}
              <Typography.Text type="secondary">最多可以复制给 200 名用户</Typography.Text>
              {targetError && <div className="inline-error" role="alert">{targetError}</div>}
              {targetFailures.length > 0 && (
                <div className="inline-error target-failures" role="alert">
                  {targetFailures.map((failure) => <div key={failure.key}>{failure.name}：{failure.reason}</div>)}
                  <div>未通过校验的员工已跳过，可调整对象后重新提交。</div>
                </div>
              )}
            </section>

            <div className="modal-footer">
              <Button onClick={resetCopyState}>取消</Button>
              <Button type="primary" onClick={submitCopy}>确认复制</Button>
            </div>
          </>
        )}
      </Modal>

      <Modal
        className="employee-picker-modal"
        title="选择员工"
        open={pickerOpen}
        width={760}
        footer={null}
        onCancel={() => setPickerOpen(false)}
        destroyOnHidden
      >
        <Typography.Text type="secondary">仅展示已加入且已完成实名认证的员工</Typography.Text>
        <div className="employee-picker-list">
          {eligibleEmployees.map((employee) => {
            const checked = stagedEmployeeKeys.has(employee.key);
            const limitReached = stagedEmployeeKeys.size >= 200 && !checked;
            return (
              <label className="employee-picker-row" key={employee.key}>
                <Checkbox
                  checked={checked}
                  disabled={limitReached}
                  onChange={(event) => {
                    setStagedEmployeeKeys((current) => {
                      const next = new Set(current);
                      if (event.target.checked && next.size < 200) next.add(employee.key);
                      else next.delete(employee.key);
                      return next;
                    });
                  }}
                />
                <span className="employee-picker-name">{employee.name}</span>
                <span className="employee-picker-phone">{employee.phone}</span>
                <span className="employee-picker-department">{employee.department}</span>
                {employee.isSubadmin && <span className="employee-current-role">已有子管理员</span>}
              </label>
            );
          })}
        </div>
        <div className="picker-summary">
          <Typography.Text type="secondary">已选 {stagedEmployeeKeys.size} 人</Typography.Text>
          <Space>
            <Button onClick={() => setPickerOpen(false)}>取消</Button>
            <Button type="primary" onClick={() => {
              setSelectedEmployeeKeys(Array.from(stagedEmployeeKeys));
              setTargetError("");
              setTargetFailures([]);
              setPickerOpen(false);
            }}>确认选择</Button>
          </Space>
        </div>
      </Modal>
    </XftApplicationFrame>
  );
}
