import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import {
  XftButton,
  type XftButtonVariant,
} from "../../../vendor/ant6-subset/adapters/xft-button";
import { Ant6SubsetButton } from "../../../vendor/ant6-subset/components/button";
import { XftSelect } from "../../../vendor/ant6-subset/adapters/xft-select";
import { XftDateField } from "../../../vendor/ant6-subset/adapters/xft-date-field";
import {
  XftTable,
  type XftTableColumn,
  type XftTableRow,
} from "../../../vendor/ant6-subset/adapters/xft-table";
import { XftStatusTag } from "../../../vendor/ant6-subset/adapters/xft-status-tag";
import { XftModal } from "../../../vendor/ant6-subset/adapters/xft-modal";
import { Button } from "../../primitives/button";
import { SelectField } from "../../primitives/select-field";
import { DateField } from "../../primitives/date-field";
import { StatusTag } from "../../primitives/status-tag";
import { DataTable } from "../../primitives/data-table";
import { Panel } from "../../primitives/panel";
import { PageHeader } from "../../compositions/page-header";
import { FilterBar } from "../../compositions/filter-bar";
import { ActionBar } from "../../compositions/action-bar";
import { DetailSection } from "../../compositions/detail-section";
import { SummaryStrip } from "../../compositions/summary-strip";
import { AdminSideShell } from "../../shells/admin-side-shell";
import { ModalTask } from "../../overlays/modal-task";
import { componentRegistry } from "../../registry/component-registry";
import { compositionRegistry } from "../../registry/composition-registry";
import { shellRegistry } from "../../registry/shell-registry";

type TabId =
  | "vendor"
  | "primitives"
  | "compositions"
  | "shells"
  | "overlays"
  | "registry"
  | "coverage";

type NavItem = {
  id: string;
  label: string;
  hint: string;
};

type TabMeta = {
  label: string;
  count: number;
  summary: string;
};

type DemoRow = XftTableRow & {
  name: string;
  status: string;
  owner: string;
};

const buttonVariants: XftButtonVariant[] = ["primary", "default", "text"];

const demoColumns: XftTableColumn<DemoRow>[] = [
  { key: "name", title: "任务名称", dataIndex: "name" },
  {
    key: "status",
    title: "状态",
    dataIndex: "status",
    render: (value) => {
      const text = String(value);
      const tone =
        text === "进行中" ? "info" : text === "已完成" ? "success" : "warning";
      return <XftStatusTag tone={tone}>{text}</XftStatusTag>;
    },
  },
  { key: "owner", title: "负责人", dataIndex: "owner" },
];

const demoRows: DemoRow[] = [
  { key: "1", name: "企业认证资料复核", status: "进行中", owner: "张敏" },
  { key: "2", name: "开票信息变更审核", status: "待确认", owner: "李原" },
  { key: "3", name: "合同归档同步", status: "已完成", owner: "王哲" },
];

const tabItems: { id: TabId; label: string }[] = [
  { id: "vendor", label: "Vendor" },
  { id: "primitives", label: "Primitives" },
  { id: "compositions", label: "Compositions" },
  { id: "shells", label: "Shells" },
  { id: "overlays", label: "Overlays" },
  { id: "registry", label: "Registry" },
  { id: "coverage", label: "Coverage" },
];

const tabMetaMap: Record<TabId, TabMeta> = {
  vendor: { label: "Vendor", count: 8, summary: "本地 Ant 子集与适配层" },
  primitives: { label: "Primitives", count: 6, summary: "正式基础资产" },
  compositions: { label: "Compositions", count: 5, summary: "固定区域模块" },
  shells: { label: "Shells", count: 1, summary: "页面级壳层" },
  overlays: { label: "Overlays", count: 1, summary: "浮层容器" },
  registry: { label: "Registry", count: 4, summary: "白名单与边界" },
  coverage: { label: "Coverage", count: 3, summary: "预览覆盖说明" },
};

const navMap: Record<TabId, NavItem[]> = {
  vendor: [
    { id: "vendor-button", label: "xft-button", hint: "按钮底层子集" },
    { id: "vendor-select", label: "xft-select", hint: "选择器底层子集" },
    { id: "vendor-date", label: "xft-date-field", hint: "日期底层子集" },
    { id: "vendor-table", label: "xft-table", hint: "表格底层子集" },
    { id: "vendor-status-tag", label: "xft-status-tag", hint: "状态语义子集" },
    { id: "vendor-modal", label: "xft-modal", hint: "基础弹层容器" },
    { id: "vendor-layout", label: "xft-layout", hint: "壳层布局底座" },
    { id: "vendor-provider", label: "xft-provider", hint: "统一主题包裹" },
  ],
  primitives: [
    { id: "primitive-button", label: "Button", hint: "正式按钮资产" },
    { id: "primitive-form", label: "Field Inputs", hint: "选择与日期字段" },
    { id: "primitive-status", label: "StatusTag", hint: "状态标签" },
    { id: "primitive-table", label: "DataTable", hint: "列表主数据区" },
    { id: "primitive-panel", label: "Panel", hint: "Surface 容器" },
  ],
  compositions: [
    { id: "composition-page-header", label: "PageHeader", hint: "页面头部模块" },
    { id: "composition-filter-bar", label: "FilterBar", hint: "筛选区模块" },
    { id: "composition-action-bar", label: "ActionBar", hint: "操作区模块" },
    { id: "composition-summary-strip", label: "SummaryStrip", hint: "摘要条模块" },
    { id: "composition-detail-section", label: "DetailSection", hint: "详情区模块" },
  ],
  shells: [
    { id: "shell-admin-side", label: "AdminSideShell", hint: "后台侧边导航壳" },
  ],
  overlays: [{ id: "overlay-modal-task", label: "ModalTask", hint: "任务弹层容器" }],
  registry: [
    { id: "registry-primitives", label: "Primitive Registry", hint: "基础资产白名单" },
    { id: "registry-compositions", label: "Composition Registry", hint: "模块白名单" },
    { id: "registry-shells", label: "Shell Registry", hint: "壳层白名单" },
    { id: "registry-props", label: "Props Contract", hint: "对外 props 白名单" },
  ],
  coverage: [
    { id: "coverage-matrix", label: "Coverage Matrix", hint: "预览覆盖矩阵" },
    { id: "coverage-example", label: "Example Coverage", hint: "组合页面覆盖" },
    { id: "coverage-system", label: "Design System", hint: "样式系统接入" },
  ],
};

function StudioSection({
  id,
  eyebrow,
  title,
  description,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="asset-studio-section">
      <div className="asset-studio-section__head">
        <span className="asset-studio-section__eyebrow">{eyebrow}</span>
        <h2 className="asset-studio-section__title">{title}</h2>
        <p className="asset-studio-section__description">{description}</p>
      </div>
      {children}
    </section>
  );
}

function ShowcaseCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <div className="asset-showcase-card">
      <div className="asset-showcase-card__head">
        <h3 className="asset-showcase-card__title">{title}</h3>
        {description ? <p className="asset-showcase-card__description">{description}</p> : null}
      </div>
      <div className="asset-showcase-card__body">{children}</div>
    </div>
  );
}

function RegistryPanel({
  title,
  items,
}: {
  title: string;
  items: ReadonlyArray<Record<string, unknown>>;
}) {
  return (
    <Panel title={title}>
      <div style={{ display: "grid", gap: "var(--space-4)" }}>
        {items.map((item) => (
          <div
            key={String(item.id)}
            style={{
              display: "grid",
              gap: "var(--space-2)",
              paddingBottom: "var(--space-4)",
              borderBottom: "1px solid var(--border-divider)",
            }}
          >
            <strong style={{ color: "var(--text-primary)" }}>{String(item.id)}</strong>
            {"summary" in item ? (
              <span style={{ color: "var(--text-tertiary)" }}>{String(item.summary)}</span>
            ) : null}
            {"allows" in item && Array.isArray(item.allows) ? (
              <span style={{ color: "var(--text-secondary)" }}>
                允许：{item.allows.join(" / ")}
              </span>
            ) : null}
            {"forbids" in item && Array.isArray(item.forbids) ? (
              <span style={{ color: "var(--text-tertiary)" }}>
                禁止：{item.forbids.join(" / ")}
              </span>
            ) : null}
          </div>
        ))}
      </div>
    </Panel>
  );
}

function PropsContractPanel() {
  const rows = [
    ["Button", "variant / disabled / loading / block / children / onClick"],
    [
      "SelectField",
      "options / placeholder / value / defaultValue / width / disabled / onValueChange",
    ],
    ["DateField", "value / defaultValue / width / disabled / min / max / onChange"],
    ["DataTable", "columns / rows / emptyText"],
    ["FilterBar", "fields / actions"],
    ["ActionBar", "primary / secondary / tools"],
    ["AdminSideShell", "title / menuItems / selectedKey / topExtra / children"],
  ] as const;

  return (
    <Panel title="Props Contract Snapshot">
      <div style={{ display: "grid", gap: "var(--space-3)" }}>
        {rows.map(([name, contract]) => (
          <div
            key={name}
            style={{
              display: "grid",
              gridTemplateColumns: "140px minmax(0, 1fr)",
              gap: "var(--space-3)",
              paddingBottom: "var(--space-3)",
              borderBottom: "1px solid var(--border-divider)",
            }}
          >
            <strong style={{ color: "var(--text-primary)" }}>{name}</strong>
            <span style={{ color: "var(--text-tertiary)" }}>{contract}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function CoverageMatrix() {
  const rows = [
    ["vendor", "xft-button / xft-select / xft-date-field / xft-table / xft-status-tag / xft-modal / xft-layout", "直接预览"],
    ["vendor", "xft-provider", "说明加生效切面覆盖"],
    ["primitives", "button / select-field / date-field / status-tag / data-table / panel", "直接预览"],
    ["compositions", "page-header / filter-bar / action-bar / detail-section / summary-strip", "直接预览"],
    ["shells", "admin-side-shell", "直接预览"],
    ["overlays", "modal-task", "直接预览"],
    ["registry", "component / composition / shell / props contract", "直接预览"],
  ] as const;

  return (
    <Panel title="Coverage Matrix">
      <div style={{ display: "grid", gap: "var(--space-3)" }}>
        {rows.map(([layer, target, status]) => (
          <div
            key={`${layer}-${target}`}
            style={{
              display: "grid",
              gridTemplateColumns: "120px minmax(0, 1fr) 240px",
              gap: "var(--space-3)",
              paddingBottom: "var(--space-3)",
              borderBottom: "1px solid var(--border-divider)",
            }}
          >
            <strong style={{ color: "var(--text-primary)" }}>{layer}</strong>
            <span style={{ color: "var(--text-secondary)" }}>{target}</span>
            <span style={{ color: "var(--text-tertiary)" }}>{status}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function SidebarStats({ activeTab, currentNavItems }: { activeTab: TabId; currentNavItems: NavItem[] }) {
  const meta = tabMetaMap[activeTab];

  return (
    <div className="asset-studio__stats">
      <div className="asset-studio__stat-card">
        <span className="asset-studio__stat-label">当前层级</span>
        <strong className="asset-studio__stat-value">{meta.label}</strong>
        <span className="asset-studio__stat-hint">{meta.summary}</span>
      </div>
      <div className="asset-studio__stat-card">
        <span className="asset-studio__stat-label">导航条目</span>
        <strong className="asset-studio__stat-value">{currentNavItems.length}</strong>
        <span className="asset-studio__stat-hint">左侧锚点与当前 tab 一一对应</span>
      </div>
    </div>
  );
}

function VendorTab({
  selectValue,
  setSelectValue,
  dateValue,
  setDateValue,
  openVendorModal,
}: {
  selectValue: string;
  setSelectValue: (value: string) => void;
  dateValue: string;
  setDateValue: (value: string) => void;
  openVendorModal: () => void;
}) {
  return (
    <>
      <StudioSection
        id="vendor-button"
        eyebrow="Vendor"
        title="xft-button"
        description="按钮底层子集只保留原型生成高频能力，不把复杂按钮 API 直接暴露给上层。"
      >
        <ShowcaseCard title="按钮变体" description="第一阶段保留 primary、default、text 三个语义变体。">
          <div className="asset-showcase-row">
            {buttonVariants.map((variant) => (
              <XftButton key={variant} variant={variant}>
                {variant}
              </XftButton>
            ))}
            <XftButton variant="primary" loading>
              加载中
            </XftButton>
          </div>
        </ShowcaseCard>
        <ShowcaseCard
          title="Raw / Adapter / Primitive"
          description="这里直接展示 components 原始层、adapter 层、primitive 层三层对照。"
        >
          <div className="asset-showcase-grid asset-showcase-grid--three">
            <Panel title="Raw Component">
              <div style={{ display: "grid", gap: "var(--space-3)" }}>
                <div className="asset-showcase-row">
                  <Ant6SubsetButton variant="primary">原始层</Ant6SubsetButton>
                  <Ant6SubsetButton>按钮</Ant6SubsetButton>
                </div>
                <div className="asset-showcase-row">
                  <Ant6SubsetButton loading>加载态</Ant6SubsetButton>
                </div>
              </div>
            </Panel>
            <Panel title="Adapter">
              <div style={{ display: "grid", gap: "var(--space-3)" }}>
                <div className="asset-showcase-row">
                  <XftButton variant="primary">xft-button</XftButton>
                  <XftButton>adapter</XftButton>
                </div>
                <div className="asset-showcase-row">
                  <XftButton loading>加载态</XftButton>
                </div>
              </div>
            </Panel>
            <Panel title="Primitive">
              <div style={{ display: "grid", gap: "var(--space-3)" }}>
                <div className="asset-showcase-row">
                  <Button variant="primary">Button</Button>
                  <Button>primitive</Button>
                </div>
                <div className="asset-showcase-row">
                  <Button loading>加载态</Button>
                </div>
              </div>
            </Panel>
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-select" eyebrow="Vendor" title="xft-select" description="底层选择器子集只服务正式 SelectField，不承载远程搜索、多选和复杂过滤。">
        <ShowcaseCard title="单选器展示">
          <div className="asset-showcase-row">
            <XftSelect
              options={[
                { label: "进行中", value: "processing" },
                { label: "待确认", value: "pending" },
                { label: "已完成", value: "done" },
              ]}
              value={selectValue}
              onValueChange={setSelectValue}
              placeholder="任务状态"
              width={180}
            />
            <XftSelect
              options={[
                { label: "张敏", value: "zhang" },
                { label: "李原", value: "li" },
                { label: "王哲", value: "wang" },
              ]}
              placeholder="负责人"
              width={180}
            />
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-date" eyebrow="Vendor" title="xft-date-field" description="底层日期字段聚焦输入能力，不扩展成复杂日期面板系统。">
        <ShowcaseCard title="日期字段展示">
          <div className="asset-showcase-row">
            <XftDateField value={dateValue} onChange={setDateValue} />
            <XftDateField defaultValue="2026-07-01" />
            <XftDateField disabled />
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-table" eyebrow="Vendor" title="xft-table" description="底层表格只保留列、行、空态和单元格渲染能力。">
        <ShowcaseCard title="表格展示">
          <XftTable columns={demoColumns} rows={demoRows} />
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-status-tag" eyebrow="Vendor" title="xft-status-tag" description="状态标签是语义色收口点，向上服务 primitives 与摘要类模块。">
        <ShowcaseCard title="状态标签展示" description="保持 tone 白名单，不允许任意颜色扩散。">
          <div className="asset-showcase-row">
            <XftStatusTag tone="info">进行中</XftStatusTag>
            <XftStatusTag tone="warning">待确认</XftStatusTag>
            <XftStatusTag tone="success">已完成</XftStatusTag>
            <XftStatusTag tone="error">异常</XftStatusTag>
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-modal" eyebrow="Vendor" title="xft-modal" description="基础弹层只负责标题、内容、关闭和 footer 容器，不承担业务流程。">
        <ShowcaseCard title="底层弹层" description="点击按钮打开基础 xft-modal。">
          <Button variant="primary" onClick={openVendorModal}>
            打开底层弹层
          </Button>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-layout" eyebrow="Vendor" title="xft-layout" description="布局子集服务壳层实现，不向上暴露通用布局引擎式能力。">
        <ShowcaseCard title="壳层布局片段">
          <div style={{ border: "1px solid var(--border-divider)", overflow: "hidden", borderRadius: "var(--radius-lg)" }}>
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
              <Panel title="壳内内容">
                <p style={{ margin: 0, color: "var(--text-tertiary)" }}>这里主要确认壳层骨架、导航态和顶部附加区是否成立。</p>
              </Panel>
            </AdminSideShell>
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="vendor-provider" eyebrow="Vendor" title="xft-provider" description="Provider 不单独出业务 UI，而是把 token、theme 和边界约束统一注入给整页资产。">
        <ShowcaseCard title="Provider 说明" description="当前预览页已经在最外层通过 DesignSystemProvider 到 XftDesignProvider 的链路包裹。">
          <div className="asset-note">这里不是单独渲染一个可见组件，而是确认下游资产的边界、间距、颜色和层级已经统一消费样式系统。</div>
        </ShowcaseCard>
      </StudioSection>
    </>
  );
}

function PrimitiveTab({
  selectValue,
  setSelectValue,
  dateValue,
  setDateValue,
}: {
  selectValue: string;
  setSelectValue: (value: string) => void;
  dateValue: string;
  setDateValue: (value: string) => void;
}) {
  return (
    <>
      <StudioSection id="primitive-button" eyebrow="Primitive" title="Button" description="正式按钮资产对外只暴露最小 props 白名单。">
        <ShowcaseCard title="按钮资产">
          <div className="asset-showcase-row">
            <Button variant="primary">主按钮</Button>
            <Button>默认按钮</Button>
            <Button variant="text">文字按钮</Button>
            <Button variant="primary" loading>
              保存中
            </Button>
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="primitive-form" eyebrow="Primitive" title="SelectField / DateField" description="这两个字段资产负责筛选区和轻表单的基础交互。">
        <ShowcaseCard title="字段资产">
          <div className="asset-showcase-row">
            <SelectField
              options={[
                { label: "进行中", value: "processing" },
                { label: "待确认", value: "pending" },
                { label: "已完成", value: "done" },
              ]}
              value={selectValue}
              onValueChange={setSelectValue}
              placeholder="任务状态"
              width={180}
            />
            <DateField value={dateValue} onChange={setDateValue} />
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="primitive-status" eyebrow="Primitive" title="StatusTag" description="状态标签封装 tone 语义，不允许任意自定义色扩散。">
        <ShowcaseCard title="标签资产">
          <div className="asset-showcase-row">
            <StatusTag tone="info">进行中</StatusTag>
            <StatusTag tone="warning">待确认</StatusTag>
            <StatusTag tone="success">已完成</StatusTag>
            <StatusTag tone="error">异常</StatusTag>
          </div>
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="primitive-table" eyebrow="Primitive" title="DataTable" description="表格资产是列表页主数据区的标准载体。">
        <ShowcaseCard title="表格资产">
          <DataTable columns={demoColumns} rows={demoRows} />
        </ShowcaseCard>
      </StudioSection>

      <StudioSection id="primitive-panel" eyebrow="Primitive" title="Panel" description="Panel 是最常见的 surface，负责承接模块边界。">
        <ShowcaseCard title="Panel 展示">
          <Panel title="资产说明" extra={<Button variant="text">更多</Button>}>
            <p style={{ margin: 0, color: "var(--text-tertiary)" }}>所有需要视觉边界的功能块，优先用 Panel 承载，而不是随意写大 padding 容器。</p>
          </Panel>
        </ShowcaseCard>
      </StudioSection>
    </>
  );
}

function CompositionTab({
  selectValue,
  setSelectValue,
  dateValue,
  setDateValue,
}: {
  selectValue: string;
  setSelectValue: (value: string) => void;
  dateValue: string;
  setDateValue: (value: string) => void;
}) {
  return (
    <>
      <StudioSection id="composition-page-header" eyebrow="Composition" title="PageHeader" description="页面标题、描述和顶层动作的固定模块。">
        <ShowcaseCard title="页头模块">
          <PageHeader title="任务管理" description="用于查询、跟进与处理当前业务任务。" actions={<Button variant="primary">新建任务</Button>} />
        </ShowcaseCard>
      </StudioSection>
      <StudioSection id="composition-filter-bar" eyebrow="Composition" title="FilterBar" description="筛选字段与查询动作的固定区域模块。">
        <ShowcaseCard title="筛选区模块">
          <FilterBar
            fields={[
              <SelectField
                key="status"
                options={[
                  { label: "进行中", value: "processing" },
                  { label: "待确认", value: "pending" },
                  { label: "已完成", value: "done" },
                ]}
                value={selectValue}
                onValueChange={setSelectValue}
                placeholder="任务状态"
                width={180}
              />,
              <DateField key="date" value={dateValue} onChange={setDateValue} />,
            ]}
            actions={
              <div className="asset-showcase-row asset-showcase-row--tight">
                <Button>重置</Button>
                <Button variant="primary">查询</Button>
              </div>
            }
          />
        </ShowcaseCard>
      </StudioSection>
      <StudioSection id="composition-action-bar" eyebrow="Composition" title="ActionBar" description="结果集批量操作和辅助工具的固定区域模块。">
        <ShowcaseCard title="操作区模块">
          <ActionBar primary={<Button variant="primary">批量处理</Button>} secondary={[<Button key="export">导出</Button>]} tools={[<Button key="columns" variant="text">列设置</Button>]} />
        </ShowcaseCard>
      </StudioSection>
      <StudioSection id="composition-summary-strip" eyebrow="Composition" title="SummaryStrip" description="摘要指标和关键状态的顶部模块。">
        <ShowcaseCard title="摘要条模块">
          <SummaryStrip items={[{ label: "总任务数", value: "128" }, { label: "进行中", value: "36", tone: "info" }, { label: "已完成", value: "92", tone: "success" }]} />
        </ShowcaseCard>
      </StudioSection>
      <StudioSection id="composition-detail-section" eyebrow="Composition" title="DetailSection" description="单对象详情阅读模块，不承担筛选和批量操作。">
        <ShowcaseCard title="详情区模块">
          <DetailSection
            title="任务详情"
            description="详情区围绕单一对象展开，可拆为多个 section，但主线必须唯一。"
            sections={[
              { title: "基础信息", items: [{ label: "任务名称", value: "企业认证资料复核" }, { label: "负责人", value: "张敏" }] },
              { title: "状态信息", items: [{ label: "当前状态", value: <StatusTag tone="info">进行中</StatusTag> }, { label: "最近更新", value: "今天 10:24" }] },
            ]}
          />
        </ShowcaseCard>
      </StudioSection>
    </>
  );
}

function ShellTab() {
  return (
    <StudioSection id="shell-admin-side" eyebrow="Shell" title="AdminSideShell" description="后台默认侧边导航型页面壳，是当前正式壳层资产。">
      <ShowcaseCard title="页面壳展示">
        <div style={{ border: "1px solid var(--border-divider)", overflow: "hidden", borderRadius: "var(--radius-lg)" }}>
          <AdminSideShell title="XFT 工作台" selectedKey="tasks" menuItems={[{ key: "dashboard", label: "概览" }, { key: "tasks", label: "任务管理" }, { key: "settings", label: "设置" }]} topExtra={<Button>帮助</Button>}>
            <Panel title="壳内内容">
              <p style={{ margin: 0, color: "var(--text-tertiary)" }}>这里主要确认壳层主布局、选中导航态和顶部附加区是否正常。</p>
            </Panel>
          </AdminSideShell>
        </div>
      </ShowcaseCard>
    </StudioSection>
  );
}

function OverlayTab({ openTaskModal }: { openTaskModal: () => void }) {
  return (
    <StudioSection id="overlay-modal-task" eyebrow="Overlay" title="ModalTask" description="正式 overlay 层当前只有这一个任务弹层容器。">
      <ShowcaseCard title="弹层容器展示" description="点击按钮打开正式 modal-task，而不是底层 xft-modal。">
        <div className="asset-showcase-row">
          <Button variant="primary" onClick={openTaskModal}>打开任务弹层</Button>
        </div>
      </ShowcaseCard>
    </StudioSection>
  );
}

function RegistryTab() {
  return (
    <>
      <StudioSection id="registry-primitives" eyebrow="Registry" title="Primitive Registry" description="这里定义正式基础资产允许被 agent 消费的白名单。">
        <RegistryPanel title="Primitive Registry" items={componentRegistry} />
      </StudioSection>
      <StudioSection id="registry-compositions" eyebrow="Registry" title="Composition Registry" description="这里定义固定区域模块的适用场景和允许能力。">
        <RegistryPanel title="Composition Registry" items={compositionRegistry} />
      </StudioSection>
      <StudioSection id="registry-shells" eyebrow="Registry" title="Shell Registry" description="这里定义页面壳层可用清单。">
        <RegistryPanel title="Shell Registry" items={shellRegistry} />
      </StudioSection>
      <StudioSection id="registry-props" eyebrow="Registry" title="Props Contract" description="这部分明确对外暴露给 agent 的 props 白名单。">
        <PropsContractPanel />
      </StudioSection>
    </>
  );
}

function CoverageTab() {
  return (
    <>
      <StudioSection id="coverage-matrix" eyebrow="Coverage" title="Preview Coverage Matrix" description="明确告诉你当前哪些是直接预览，哪些是说明加生效切面覆盖。">
        <CoverageMatrix />
      </StudioSection>
      <StudioSection id="coverage-example" eyebrow="Coverage" title="Example Coverage" description="示例页不再单独堆一个大页面，而是由组合模块和壳层共同覆盖。">
        <ShowcaseCard title="为什么不再单独堆一个示例页">
          <div className="asset-note">当前预览台的目标是按资产层级检查组件和模块，而不是把完整业务页再重复堆一遍。列表管理页的核心能力已经被 PageHeader、FilterBar、ActionBar、DataTable、AdminSideShell 这些正式资产组合覆盖。</div>
        </ShowcaseCard>
      </StudioSection>
      <StudioSection id="coverage-system" eyebrow="Coverage" title="Design System Coverage" description="设计系统不是单独视觉组件，而是通过整页样式和配方间接生效。">
        <ShowcaseCard title="样式系统接入说明">
          <div className="asset-note">当前预览页已经统一消费 tokens.css、token-recipes、component-recipes 和主题桥接，所以你在这里看到的边界、间距、颜色和层级，就是 design-systems 的实际落地结果。</div>
        </ShowcaseCard>
      </StudioSection>
    </>
  );
}

function TabContent(props: {
  activeTab: TabId;
  selectValue: string;
  setSelectValue: (value: string) => void;
  dateValue: string;
  setDateValue: (value: string) => void;
  openVendorModal: () => void;
  openTaskModal: () => void;
}) {
  const { activeTab, selectValue, setSelectValue, dateValue, setDateValue, openVendorModal, openTaskModal } = props;
  switch (activeTab) {
    case "vendor":
      return <VendorTab selectValue={selectValue} setSelectValue={setSelectValue} dateValue={dateValue} setDateValue={setDateValue} openVendorModal={openVendorModal} />;
    case "primitives":
      return <PrimitiveTab selectValue={selectValue} setSelectValue={setSelectValue} dateValue={dateValue} setDateValue={setDateValue} />;
    case "compositions":
      return <CompositionTab selectValue={selectValue} setSelectValue={setSelectValue} dateValue={dateValue} setDateValue={setDateValue} />;
    case "shells":
      return <ShellTab />;
    case "overlays":
      return <OverlayTab openTaskModal={openTaskModal} />;
    case "registry":
      return <RegistryTab />;
    case "coverage":
      return <CoverageTab />;
    default:
      return null;
  }
}

export function AssetPreviewPage() {
  const [activeTab, setActiveTab] = useState<TabId>("vendor");
  const [activeAnchor, setActiveAnchor] = useState(navMap.vendor[0].id);
  const [vendorModalOpen, setVendorModalOpen] = useState(false);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [selectValue, setSelectValue] = useState("processing");
  const [dateValue, setDateValue] = useState("2026-07-12");

  const currentNavItems = useMemo(() => navMap[activeTab], [activeTab]);

  useEffect(() => {
    setActiveAnchor(currentNavItems[0].id);
    requestAnimationFrame(() => {
      document.getElementById(currentNavItems[0].id)?.scrollIntoView({ block: "start" });
    });
  }, [activeTab, currentNavItems]);

  useEffect(() => {
    const sections = currentNavItems.map((item) => document.getElementById(item.id)).filter((node): node is HTMLElement => Boolean(node));
    if (sections.length === 0) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntries = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visibleEntries[0]?.target.id) setActiveAnchor(visibleEntries[0].target.id);
      },
      { rootMargin: "-120px 0px -55% 0px", threshold: [0.2, 0.4, 0.6] },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [activeTab, currentNavItems]);

  const jumpToSection = (id: string) => {
    setActiveAnchor(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="asset-studio">
      <header className="asset-studio__topbar">
        <div className="asset-studio__brand">
          <span className="asset-studio__eyebrow">XFT Design</span>
          <strong className="asset-studio__title">Asset Studio</strong>
        </div>
        <div className="asset-studio__tabs">
          {tabItems.map((tab) => (
            <button key={tab.id} type="button" className={tab.id === activeTab ? "asset-studio__tab asset-studio__tab--active" : "asset-studio__tab"} onClick={() => setActiveTab(tab.id)}>
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      <div className="asset-studio__layout">
        <aside className="asset-studio__sidebar">
          <div className="asset-studio__sidebar-head">
            <span className="asset-studio__sidebar-kicker">{tabMetaMap[activeTab].label}</span>
            <h1 className="asset-studio__sidebar-title">资产预览导航</h1>
            <p className="asset-studio__sidebar-description">顶部负责切换资产层级，左侧负责切换当前层级下的具体资产，右侧展示真实预览。</p>
          </div>
          <SidebarStats activeTab={activeTab} currentNavItems={currentNavItems} />
          <div className="asset-studio__sidebar-list">
            {currentNavItems.map((item) => (
              <button key={item.id} type="button" className={item.id === activeAnchor ? "asset-studio__anchor asset-studio__anchor--active" : "asset-studio__anchor"} onClick={() => jumpToSection(item.id)}>
                <span className="asset-studio__anchor-label">{item.label}</span>
                <span className="asset-studio__anchor-hint">{item.hint}</span>
              </button>
            ))}
          </div>
        </aside>

        <main className="asset-studio__content">
          <section className="asset-studio__intro">
            <PageHeader title="XFT Asset Preview" description="用一个轻量但结构清晰的预览台，检查 vendor、正式资产层和规则暴露面。" actions={<Button variant="primary" onClick={() => setVendorModalOpen(true)}>打开底层弹层</Button>} />
          </section>

          <TabContent activeTab={activeTab} selectValue={selectValue} setSelectValue={setSelectValue} dateValue={dateValue} setDateValue={setDateValue} openVendorModal={() => setVendorModalOpen(true)} openTaskModal={() => setTaskModalOpen(true)} />
        </main>
      </div>

      <XftModal open={vendorModalOpen} title="底层 xft-modal" onClose={() => setVendorModalOpen(false)} footer={<Button onClick={() => setVendorModalOpen(false)}>关闭</Button>}>
        <p style={{ margin: 0, color: "var(--text-tertiary)" }}>这个弹层用于确认底层 xft-modal 是否可见、可交互。</p>
      </XftModal>

      <ModalTask open={taskModalOpen} title="任务弹层" footer={<Button onClick={() => setTaskModalOpen(false)}>关闭</Button>} onClose={() => setTaskModalOpen(false)}>
        <p style={{ margin: 0, color: "var(--text-tertiary)" }}>这里直接预览的是 modal-task overlay，而不是底层 xft-modal。</p>
      </ModalTask>
    </div>
  );
}
