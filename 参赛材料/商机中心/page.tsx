import { useMemo, useState } from "react";
import type { Key } from "react";
import { createRoot } from "react-dom/client";
import {
  Alert, Button, Checkbox, ConfigProvider, DatePicker, Descriptions, Input,
  Modal, Pagination, Select, Space, Table, Tabs, Tag, Typography, message
} from "antd";
import type { TableColumnsType } from "antd";
import { themeConfig } from "./theme/theme-config.generated.mjs";
import { WealthPlusApplicationFrame } from "./page-assets/template.wealth-plus.application-frame/WealthPlusApplicationFrame";
import "./styles.css";

type Screen = "strategy-list" | "strategy-detail" | "customer-list" | "customer-detail" | "data-review";

type StrategyRow = {
  key: string;
  name: string;
  category: string;
  summary: string;
  priority: "高" | "中";
  due: string;
  channel: string;
  material: string;
  current: number;
  newCount: number;
  expiring: number;
};

type OpportunityRow = {
  key: string;
  customer: string;
  customerNo: string;
  opportunity: string;
  strategyKey: string;
  count: number;
  due: string;
  dueState: "soon" | "normal" | "overdue";
  status: string;
  publicStar: string;
  wealthStar: string;
  balance: string;
  branch: string;
  manager: string;
};

const strategies: StrategyRow[] = [
  { key: "s1", name: "高潜活期留存提升", category: "资金留存", summary: "近 30 日活期日均余额达到规则阈值，且近 7 日存在明显资金波动", priority: "高", due: "3 天", channel: "客户经理", material: "资产配置建议", current: 428, newCount: 36, expiring: 18 },
  { key: "s2", name: "大额到期承接", category: "产品到期", summary: "未来 7 日存在大额产品到期，当前尚无明确承接产品记录", priority: "高", due: "7 天", channel: "客户经理", material: "到期承接方案", current: 286, newCount: 22, expiring: 31 },
  { key: "s3", name: "结构性存款到期", category: "产品到期", summary: "结构性存款进入到期观察期，需结合风险偏好重新匹配方案", priority: "中", due: "7 天", channel: "企微", material: "产品到期提醒", current: 193, newCount: 14, expiring: 27 },
  { key: "s4", name: "结算资金增值", category: "资金增值", summary: "结算账户沉淀资金持续高于经营周转需求，可进一步识别增值需求", priority: "中", due: "14 天", channel: "电话", material: "现金管理方案", current: 379, newCount: 12, expiring: 9 }
];

const customers: OpportunityRow[] = [
  { key: "1", customer: "华东某科技集团有限公司", customerNo: "6218 **** 3086", opportunity: "高潜活期留存提升", strategyKey: "s1", count: 3, due: "剩余 2 天", dueState: "soon", status: "新进入", publicStar: "五星", wealthStar: "四星", balance: "¥ 28,650,000", branch: "上海分行", manager: "林经理" },
  { key: "2", customer: "中汇智能制造有限公司", customerNo: "6218 **** 6721", opportunity: "大额到期承接", strategyKey: "s2", count: 2, due: "剩余 5 天", dueState: "normal", status: "持续命中", publicStar: "五星", wealthStar: "五星", balance: "¥ 16,320,000", branch: "深圳分行", manager: "周经理" },
  { key: "3", customer: "南方新材料股份有限公司", customerNo: "6218 **** 1193", opportunity: "结构性存款到期", strategyKey: "s3", count: 4, due: "今日到期", dueState: "soon", status: "即将到期", publicStar: "四星", wealthStar: "四星", balance: "¥ 9,870,000", branch: "广州分行", manager: "陈经理" },
  { key: "4", customer: "北辰供应链管理有限公司", customerNo: "6218 **** 8540", opportunity: "结算资金增值", strategyKey: "s4", count: 1, due: "已超期 1 天", dueState: "overdue", status: "已超期", publicStar: "三星", wealthStar: "--", balance: "¥ 6,480,000", branch: "北京分行", manager: "未分配" },
  { key: "5", customer: "远海医药科技有限公司", customerNo: "6218 **** 4468", opportunity: "高潜活期留存提升", strategyKey: "s1", count: 2, due: "剩余 7 天", dueState: "normal", status: "持续命中", publicStar: "三星", wealthStar: "三星", balance: "¥ 4,260,000", branch: "杭州分行", manager: "王经理" }
];

const statusClass: Record<string, string> = {
  "新进入": "status-new", "持续命中": "status-active", "即将到期": "status-warning", "已超期": "status-overdue"
};

const screenGroup = (screen: Screen) => screen.startsWith("strategy") ? "rules" : screen.startsWith("customer") ? "marketing" : "review";
const screenPaths: Record<Screen, string> = {
  "strategy-list": "strategy-list.html",
  "strategy-detail": "strategy-detail.html",
  "customer-list": "customer-list.html",
  "customer-detail": "customer-detail.html",
  "data-review": "data-review.html"
};

function routeHref(screen: Screen, params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  return query ? `${screenPaths[screen]}?${query}` : screenPaths[screen];
}

function initialScreen(): Screen {
  if (typeof window === "undefined") return "strategy-list";
  const declared = document.documentElement.dataset.screen as Screen | undefined;
  if (declared && screenPaths[declared]) return declared;
  const filename = window.location.pathname.split("/").pop();
  const fromFilename = (Object.entries(screenPaths).find(([, path]) => path === filename)?.[0]) as Screen | undefined;
  if (fromFilename) return fromFilename;
  const candidate = new URLSearchParams(window.location.search).get("screen") as Screen | null;
  return candidate && ["strategy-list", "strategy-detail", "customer-list", "customer-detail", "data-review"].includes(candidate) ? candidate : "strategy-list";
}

export function GeneratedPage() {
  const [screen, setScreen] = useState<Screen>(initialScreen);
  const [customerTab, setCustomerTab] = useState("pending");
  const [selectedStrategyKey, setSelectedStrategyKey] = useState(() => typeof window === "undefined" ? "s1" : new URLSearchParams(window.location.search).get("strategy") ?? "s1");
  const [selectedCustomerKey, setSelectedCustomerKey] = useState(() => typeof window === "undefined" ? "1" : new URLSearchParams(window.location.search).get("customer") ?? "1");
  const [selectedCustomerKeys, setSelectedCustomerKeys] = useState<Key[]>([]);
  const [branch, setBranch] = useState<string>();
  const [strategyFilter, setStrategyFilter] = useState<string>();
  const [keyword, setKeyword] = useState("");
  const [appliedKeyword, setAppliedKeyword] = useState("");
  const [marketingOpen, setMarketingOpen] = useState(false);
  const [skipIntro, setSkipIntro] = useState(false);
  const [checking, setChecking] = useState(false);
  const [marketingCount, setMarketingCount] = useState(1);

  const navigate = (next: Screen, params: Record<string, string> = {}) => {
    window.location.href = routeHref(next, params);
  };

  const selectedStrategy = strategies.find((item) => item.key === selectedStrategyKey) ?? strategies[0];
  const selectedCustomer = customers.find((item) => item.key === selectedCustomerKey) ?? customers[0];

  const filteredCustomers = useMemo(() => customers.filter((row) => {
    const keywordMatched = !appliedKeyword || `${row.customer}${row.customerNo}${row.manager}`.includes(appliedKeyword);
    return keywordMatched && (!branch || row.branch === branch) && (!strategyFilter || row.strategyKey === strategyFilter);
  }), [appliedKeyword, branch, strategyFilter]);

  const queryCustomers = () => {
    setAppliedKeyword(keyword.trim());
    message.success("已按当前权限和最新数据刷新客户列表");
  };

  const resetCustomers = () => {
    setBranch(undefined);
    setStrategyFilter(undefined);
    setKeyword("");
    setAppliedKeyword("");
    setSelectedCustomerKeys([]);
  };

  const toggleCustomerSelection = (key: Key, checked: boolean) => {
    setSelectedCustomerKeys((current) => checked ? [...current, key] : current.filter((item) => item !== key));
  };

  const openMarketing = (count = 1) => {
    setMarketingCount(count);
    setMarketingOpen(true);
  };

  const confirmMarketing = () => {
    setChecking(true);
    window.setTimeout(() => {
      setChecking(false);
      setMarketingOpen(false);
      message.success(`已完成 ${marketingCount} 位客户的 CRM 权限校验，正在进入乘流`);
    }, 800);
  };

  const openStrategyDetail = (row: StrategyRow) => {
    setSelectedStrategyKey(row.key);
    setSelectedCustomerKeys([]);
    navigate("strategy-detail", { strategy: row.key });
  };

  const openCustomerDetail = (row: OpportunityRow) => {
    setSelectedCustomerKey(row.key);
    navigate("customer-detail", { customer: row.key });
  };

  const strategyColumns: TableColumnsType<StrategyRow> = [
    { title: "策略包名称", dataIndex: "name", key: "name", width: 210, render: (value, row) => <a className="table-link" href={routeHref("strategy-detail", { strategy: row.key })}>{value}</a> },
    { title: "分类", dataIndex: "category", key: "category", width: 112 },
    { title: "商机规则摘要", dataIndex: "summary", key: "summary", width: 360, ellipsis: true },
    { title: "优先级", dataIndex: "priority", key: "priority", width: 88, render: (value) => <Tag className={value === "高" ? "status-new" : "status-neutral"}>{value}</Tag> },
    { title: "跟进期限", dataIndex: "due", key: "due", width: 96 },
    { title: "建议渠道", dataIndex: "channel", key: "channel", width: 112 },
    { title: "当前客户", dataIndex: "current", key: "current", width: 104, align: "right", className: "number-cell" },
    { title: "新进入", dataIndex: "newCount", key: "newCount", width: 88, align: "right", className: "number-cell" },
    { title: "即将过期", dataIndex: "expiring", key: "expiring", width: 104, align: "right", className: "number-cell" },
    { title: "操作", key: "actions", fixed: "right", width: 80, render: (_, row) => <a className="table-link" href={routeHref("strategy-detail", { strategy: row.key })}>详情</a> }
  ];

  const customerColumns: TableColumnsType<OpportunityRow> = [
    { title: "客户名称", dataIndex: "customer", key: "customer", fixed: "left", width: 220, render: (value, row) => <a className="table-link" href={routeHref("customer-detail", { customer: row.key })}>{value}</a> },
    { title: "客户号", dataIndex: "customerNo", key: "customerNo", width: 150, className: "number-cell" },
    { title: "命中商机", dataIndex: "opportunity", key: "opportunity", width: 210, render: (value, row) => <a className="opportunity-trigger" href={routeHref("strategy-detail", { strategy: row.strategyKey })}>{value}<span>等 {row.count} 项</span></a> },
    { title: "最近过期", dataIndex: "due", key: "due", width: 120, render: (value, row) => <span className={`due-${row.dueState}`}>{value}</span> },
    { title: "命中状态", dataIndex: "status", key: "status", width: 112, render: (value) => <Tag className={statusClass[value]}>{value}</Tag> },
    { title: "公金星级", dataIndex: "publicStar", key: "publicStar", width: 104 },
    { title: "财富星级", dataIndex: "wealthStar", key: "wealthStar", width: 104 },
    { title: "当前余额", dataIndex: "balance", key: "balance", width: 152, align: "right", className: "number-cell" },
    { title: "分行", dataIndex: "branch", key: "branch", width: 112 },
    { title: "客户经理", dataIndex: "manager", key: "manager", width: 104 },
    { title: "操作", key: "actions", fixed: "right", width: 80, render: (_, row) => <a className="table-link" href={routeHref("customer-detail", { customer: row.key })}>详情</a> }
  ];

  const moduleTabs = <Tabs className="module-tabs" activeKey={screenGroup(screen)} items={[
    { key: "rules", label: <a href={screenPaths["strategy-list"]}>商机策略</a> },
    { key: "marketing", label: <a href={screenPaths["customer-list"]}>商机客户</a> },
    { key: "review", label: <a href={screenPaths["data-review"]}>数据回检</a> }
  ]} />;

  const heading = (title: string, description: string, back?: { label: string; screen: Screen }) => <>
    {back ? <a className="back-link" href={screenPaths[back.screen]}>← {back.label}</a> : null}
    <div className="page-heading-row"><div><Typography.Title level={4} className="page-title">{title}</Typography.Title><Typography.Text className="page-description">{description}</Typography.Text></div><div className="update-time">数据更新：2026-08-05 09:30</div></div>
  </>;

  const StrategyList = () => <>
    {heading("商机策略", "查看预置策略包、规则摘要、期限和当前客户覆盖")}
    <section className="filter-region" aria-label="策略筛选"><div className="filter-grid filter-grid--strategy">
      <Select aria-label="分类" placeholder="分类" allowClear options={["资金留存", "产品到期", "资金增值"].map((value) => ({ value, label: value }))} />
      <Select aria-label="优先级" placeholder="优先级" allowClear options={["高", "中"].map((value) => ({ value, label: value }))} />
      <Input aria-label="策略包名称" placeholder="策略包名称" allowClear />
    </div><Space className="filter-actions"><Button>重置</Button><Button type="primary" onClick={() => message.success("策略包列表已刷新")}>查询</Button></Space></section>
    <div className="table-toolbar"><div><strong>策略包列表</strong><span>策略包由系统预置，当前不支持编辑</span></div></div>
    <div className="desktop-table"><Table<StrategyRow> rowKey="key" columns={strategyColumns} dataSource={strategies} pagination={false} scroll={{ x: 1380 }} /></div>
    <div className="mobile-list">{strategies.map((row) => <article className="mobile-customer" key={row.key}><div className="mobile-customer__top"><a href={routeHref("strategy-detail", { strategy: row.key })}>{row.name}</a><Tag className={row.priority === "高" ? "status-new" : "status-neutral"}>{row.priority}优先级</Tag></div><dl><div><dt>规则分类</dt><dd>{row.category}</dd></div><div><dt>跟进期限</dt><dd>{row.due}</dd></div><div><dt>当前客户</dt><dd>{row.current}</dd></div><div><dt>即将过期</dt><dd>{row.expiring}</dd></div></dl><a className="table-link" href={routeHref("strategy-detail", { strategy: row.key })}>查看详情</a></article>)}</div>
    <div className="pagination-row"><span>共 13 个策略包</span><Pagination current={1} total={13} pageSize={10} /></div>
  </>;

  const StrategyDetail = () => {
    const related = customers.filter((row) => row.strategyKey === selectedStrategy.key);
    const columns: TableColumnsType<OpportunityRow> = [
      { title: "客户名称", dataIndex: "customer", key: "customer", width: 240, render: (value, row) => <a className="table-link" href={routeHref("customer-detail", { customer: row.key })}>{value}</a> },
      { title: "公金星级", dataIndex: "publicStar", key: "publicStar", width: 110 },
      { title: "命中状态", dataIndex: "status", key: "status", width: 120, render: (value) => <Tag className={statusClass[value]}>{value}</Tag> },
      { title: "跟进期限", dataIndex: "due", key: "due", width: 120, render: (value, row) => <span className={`due-${row.dueState}`}>{value}</span> },
      { title: "当前余额", dataIndex: "balance", key: "balance", align: "right", width: 160, className: "number-cell" },
      { title: "客户经理", dataIndex: "manager", key: "manager", width: 110 },
      { title: "操作", key: "action", width: 150, render: (_, row) => <Space size={8}><a className="table-link" href={routeHref("customer-detail", { customer: row.key })}>详情</a><Button type="link" onClick={() => openMarketing(1)}>做营销</Button></Space> }
    ];
    return <>
      {heading(selectedStrategy.name, "策略规则、业务解释与当前命中客户", { label: "返回策略包列表", screen: "strategy-list" })}
      <section className="detail-section"><div className="detail-title"><h2>策略规则</h2><Space><Tag className={selectedStrategy.priority === "高" ? "status-new" : "status-neutral"}>{selectedStrategy.priority}优先级</Tag><Tag>只读</Tag></Space></div>
        <Descriptions column={{ xs: 1, sm: 1, md: 2 }} items={[
          { key: "summary", label: "规则摘要", children: selectedStrategy.summary, span: 2 },
          { key: "condition", label: "命中条件", children: "最新有效数据批次满足规则阈值，且客户处于当前机构权限范围内", span: 2 },
          { key: "due", label: "跟进期限", children: selectedStrategy.due },
          { key: "channel", label: "建议渠道", children: selectedStrategy.channel },
          { key: "material", label: "建议物料", children: selectedStrategy.material },
          { key: "source", label: "数据来源", children: "企业财富+客户资产快照" }
        ]} />
      </section>
      <section className="stat-strip stat-strip--detail" aria-label="策略客户统计">{[
        ["当前客户", selectedStrategy.current], ["新进入", selectedStrategy.newCount], ["即将过期", selectedStrategy.expiring]
      ].map(([label, value]) => <div className="stat-item stat-item--static" key={String(label)}><span className="stat-label">{label}</span><strong>{value}</strong><small>最新有效快照</small></div>)}</section>
      <section className="detail-section detail-section--table"><div className="table-toolbar"><div><strong>商机客户</strong><span>{selectedCustomerKeys.length ? `已选择 ${selectedCustomerKeys.length} 位客户` : "选择客户后可批量做营销"}</span></div><Button type="primary" disabled={!selectedCustomerKeys.length} onClick={() => openMarketing(selectedCustomerKeys.length)}>批量做营销</Button></div>
        <div className="desktop-table"><Table<OpportunityRow> rowKey="key" rowSelection={{ selectedRowKeys: selectedCustomerKeys, onChange: setSelectedCustomerKeys }} columns={columns} dataSource={related.length ? related : customers.slice(0, 3)} pagination={false} scroll={{ x: 1100 }} /></div>
      </section>
    </>;
  };

  const CustomerList = () => <>
    {heading("商机客户", "按客户聚合当前有效商机，优先处理高星级与临近到期客户")}
    <section className="stat-strip" aria-label="商机客户统计">{[
      ["当前客户", "1,286", "当前权限范围"], ["公金五星", "326", "优先查看"], ["新进入", "84", "今日新增"], ["即将过期", "37", "未来 3 天"]
    ].map(([label, value, helper]) => <button key={label} className="stat-item" onClick={() => message.info(`已叠加“${label}”筛选条件`)}><span className="stat-label">{label}</span><strong>{value}</strong><small>{helper}</small></button>)}</section>
    <Tabs className="business-tabs" activeKey={customerTab} onChange={setCustomerTab} items={[
      { key: "pending", label: "待处理 1,286" }, { key: "marketing", label: "营销中 216" }, { key: "completed", label: "已完成营销 584" }, { key: "expired", label: "未营销已过期 92" }
    ]} />
    <section className="filter-region" aria-label="客户筛选"><div className="filter-grid">
      <Select aria-label="分行" placeholder="分行" allowClear value={branch} onChange={setBranch} options={["上海分行", "深圳分行", "广州分行", "北京分行", "杭州分行"].map((value) => ({ value, label: value }))} />
      <Select aria-label="策略包" placeholder="策略包" allowClear value={strategyFilter} onChange={setStrategyFilter} options={strategies.map((item) => ({ value: item.key, label: item.name }))} />
      <Select aria-label="公金星级" placeholder="公金星级" allowClear options={["五星", "四星", "三星", "二星", "一星"].map((value) => ({ value, label: value }))} />
      <Select aria-label="命中状态" placeholder="命中状态" allowClear options={["新进入", "持续命中", "即将到期", "已超期"].map((value) => ({ value, label: value }))} />
      <DatePicker.RangePicker aria-label="最近过期时间" placeholder={["最近过期开始", "最近过期结束"]} />
      <Input aria-label="客户名称、客户号或客户经理" placeholder="客户名称 / 客户号 / 客户经理" value={keyword} onChange={(event) => setKeyword(event.target.value)} onPressEnter={queryCustomers} />
    </div><Space className="filter-actions"><Button onClick={resetCustomers}>重置</Button><Button type="primary" onClick={queryCustomers}>查询</Button></Space></section>
    <div className="table-toolbar"><div><strong>商机客户列表</strong><span>{selectedCustomerKeys.length ? `已选择 ${selectedCustomerKeys.length} 位客户` : "勾选客户后可发起批量营销"}</span></div>{customerTab === "pending" ? <Button type="primary" disabled={!selectedCustomerKeys.length} onClick={() => openMarketing(selectedCustomerKeys.length)}>做营销</Button> : null}</div>
    <div className="desktop-table"><Table<OpportunityRow> rowKey="key" rowSelection={{ selectedRowKeys: selectedCustomerKeys, onChange: setSelectedCustomerKeys, preserveSelectedRowKeys: true }} columns={customerColumns} dataSource={filteredCustomers} pagination={false} scroll={{ x: 1480 }} locale={{ emptyText: "当前条件下暂无商机客户，可调整条件或重置筛选" }} /></div>
    <div className="mobile-list">{filteredCustomers.map((row) => <article className="mobile-customer" key={row.key}><div className="mobile-customer__top"><div className="mobile-customer__identity"><Checkbox aria-label={`选择${row.customer}`} checked={selectedCustomerKeys.includes(row.key)} onChange={(event) => toggleCustomerSelection(row.key, event.target.checked)} /><a href={routeHref("customer-detail", { customer: row.key })}>{row.customer}</a></div><Tag className={statusClass[row.status]}>{row.status}</Tag></div><dl><div><dt>命中商机</dt><dd>{row.opportunity}等 {row.count} 项</dd></div><div><dt>最近过期</dt><dd className={`due-${row.dueState}`}>{row.due}</dd></div><div><dt>当前余额</dt><dd>{row.balance}</dd></div><div><dt>客户经理</dt><dd>{row.manager}</dd></div></dl><a className="table-link" href={routeHref("customer-detail", { customer: row.key })}>查看详情</a></article>)}</div>
    <div className="pagination-row"><span>共 1,286 条</span><Pagination current={1} total={1286} pageSize={20} showSizeChanger showQuickJumper /></div>
  </>;

  const CustomerDetail = () => {
    const currentStrategies = strategies.filter((item) => item.key === selectedCustomer.strategyKey || item.priority === "高").slice(0, selectedCustomer.count);
    const opportunityColumns: TableColumnsType<StrategyRow> = [
      { title: "策略包", dataIndex: "name", key: "name", width: 220, render: (value, row) => <a className="table-link" href={routeHref("strategy-detail", { strategy: row.key })}>{value}</a> },
      { title: "优先级", dataIndex: "priority", key: "priority", width: 90, render: (value) => <Tag className={value === "高" ? "status-new" : "status-neutral"}>{value}</Tag> },
      { title: "命中状态", key: "status", width: 120, render: () => <Tag className={statusClass[selectedCustomer.status]}>{selectedCustomer.status}</Tag> },
      { title: "跟进期限", key: "due", width: 120, render: () => <span className={`due-${selectedCustomer.dueState}`}>{selectedCustomer.due}</span> },
      { title: "建议渠道", dataIndex: "channel", key: "channel", width: 120 },
      { title: "操作", key: "action", width: 90, render: (_, row) => <a className="table-link" href={routeHref("strategy-detail", { strategy: row.key })}>包详情</a> }
    ];
    return <>
      {heading(selectedCustomer.customer, "客户当前有效商机、命中事实与可确认营销记录", { label: "返回商机客户", screen: "customer-list" })}
      <section className="detail-section"><div className="detail-title"><h2>客户摘要</h2><Tag>{selectedCustomer.customerNo}</Tag></div><Descriptions column={{ xs: 1, sm: 2, md: 3 }} items={[
        { key: "org", label: "所属机构", children: selectedCustomer.branch }, { key: "manager", label: "客户经理", children: selectedCustomer.manager },
        { key: "stars", label: "公金 / 财富星级", children: `${selectedCustomer.publicStar} / ${selectedCustomer.wealthStar}` },
        { key: "balance", label: "当前时点余额", children: selectedCustomer.balance }, { key: "average", label: "年日均余额", children: "—" },
        { key: "highest", label: "历史最高余额", children: "统计口径待确认" }
      ]} /></section>
      <section className="detail-section detail-section--table"><div className="table-toolbar"><div><strong>当前有效商机（{selectedCustomer.count}）</strong><span>仅展示最新有效快照</span></div><Button type="primary" onClick={() => openMarketing(1)}>去做营销</Button></div><div className="desktop-table"><Table<StrategyRow> rowKey="key" columns={opportunityColumns} dataSource={currentStrategies} pagination={false} scroll={{ x: 900 }} /></div></section>
      <section className="detail-section"><div className="detail-title"><h2>CRM 营销记录</h2><span className="section-note">数据更新：2026-08-05 09:15</span></div><Alert type="info" showIcon title="暂无法确认" description="当前没有足够的 CRM 稳定关联证据，系统不会推断营销成功或失败。" /></section>
    </>;
  };

  const DataReview = () => {
    const sourceColumns: TableColumnsType<{ key: string; source: string; updated: string; coverage: string; status: string }> = [
      { title: "数据源", dataIndex: "source", key: "source", width: 220 }, { title: "数据截止时间", dataIndex: "updated", key: "updated", width: 220, className: "number-cell" },
      { title: "覆盖范围", dataIndex: "coverage", key: "coverage" }, { title: "同步状态", dataIndex: "status", key: "status", width: 140, render: (value) => <Tag className={value === "已更新" ? "status-active" : "status-warning"}>{value}</Tag> }
    ];
    const sourceRows = [
      { key: "wealth", source: "企业财富+商机数据", updated: "2026-08-05 09:30", coverage: "当前权限范围内客户", status: "已更新" },
      { key: "crm", source: "CRM 营销执行数据", updated: "2026-08-05 09:15", coverage: "具备稳定关联的营销记录", status: "已更新" },
      { key: "channel", source: "渠道触达数据", updated: "2026-08-05 08:40", coverage: "已回传触达与响应记录", status: "更新中" },
      { key: "purchase", source: "产品购买数据", updated: "2026-08-04 23:50", coverage: "观察期已结束客户", status: "已更新" }
    ];
    return <>
      {heading("数据回检", "在知几统一分析商机购买率、营销漏斗与客户执行明细")}
      <section className="review-hero"><div><h2>商机经营效果统一回检</h2><p>企业财富+负责发现和解释商机；知几负责购买率、营销发起—触达—响应漏斗及客户执行明细分析。</p></div><Button type="primary" onClick={() => message.success("知几访问权限校验通过，正在打开商机经营看板")}>去知几查看</Button></section>
      <section className="review-metrics" aria-label="回检口径"><div><span>购买率</span><strong>—</strong><small>分母口径待确认</small></div><div><span>数据覆盖率</span><strong>—</strong><small>等待渠道数据完成</small></div><div><span>未知客户</span><strong>—</strong><small>不计成功或失败</small></div><div><span>观察中</span><strong>—</strong><small>不提前判定未购买</small></div></section>
      <section className="detail-section detail-section--table"><div className="detail-title"><h2>数据源状态</h2><span className="section-note">各来源更新时间独立展示</span></div><div className="desktop-table"><Table rowKey="key" columns={sourceColumns} dataSource={sourceRows} pagination={false} /></div></section>
      <Alert className="review-note" type="info" showIcon title="回检口径说明" description="分母为 0 时指标显示“—”；未知数据不会被计为失败，观察期未结束的客户不会提前判定未购买。" />
    </>;
  };

  const renderScreen = () => {
    if (screen === "strategy-list") return <StrategyList />;
    if (screen === "strategy-detail") return <StrategyDetail />;
    if (screen === "customer-list") return <CustomerList />;
    if (screen === "customer-detail") return <CustomerDetail />;
    return <DataReview />;
  };

  return <ConfigProvider theme={{ ...themeConfig, zeroRuntime: true }}>
    <WealthPlusApplicationFrame primaryNavigationItems={[
      { key: "home", label: "首页" },
      { key: "product", label: "产品中心" },
      { key: "marketing", label: "营销中心" },
      { key: "warning", label: "预警中心" },
      { key: "opportunity", label: "商机中心" },
      { key: "config", label: "配置管理" }
    ]} activePrimaryNavigationKey="opportunity" globalActions={<Space size={16}><Button type="text">消息</Button><span className="user-identity">总行产品经理</span></Space>}>
      {moduleTabs}
      {renderScreen()}
      <Modal title="去做营销" open={marketingOpen} onCancel={() => setMarketingOpen(false)} footer={[
        <Button key="cancel" onClick={() => setMarketingOpen(false)}>取消</Button>,
        <Button key="confirm" type="primary" loading={checking} onClick={confirmMarketing}>已知晓，去做营销</Button>
      ]}><div className="marketing-intro"><p>本次将为 <strong>{marketingCount}</strong> 位客户进入 CRM 乘流。企业财富+用于发现和解释商机；CRM 用于客户选择、营销配置和执行。</p><ul><li>当前客户与筛选不会自动带入 CRM。</li><li>点击进入不代表营销已发起。</li><li>取消或跳转失败后保留当前页面上下文。</li></ul><Checkbox checked={skipIntro} onChange={(event) => setSkipIntro(event.target.checked)}>不再显示此提示</Checkbox></div></Modal>
    </WealthPlusApplicationFrame>
  </ConfigProvider>;
}

if (typeof document !== "undefined") {
  const rootElement = document.getElementById("root");
  if (!rootElement) throw new Error("Preview root #root was not found.");
  createRoot(rootElement).render(<GeneratedPage />);
}
