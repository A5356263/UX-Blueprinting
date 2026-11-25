import React, { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { Button, Checkbox, DatePicker, Input, InputNumber, Modal, Popover, Select, Tooltip } from "antd";
import { DeleteOutlined, DownOutlined, FilterOutlined, LeftOutlined, RightOutlined, SaveOutlined, SearchOutlined, SettingOutlined, UpOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { XftFilterField, XftFilterMode, XftFilterScheme, XftFilterTableBinding, XftFilterValue, XftFilterValues, XftSchemeManagerTableBinding } from "./XftFilterWorkbench.model";
import "./XftFilterWorkbench.css";

export type XftFilterWorkbenchActions = { applied: XftFilterValues; hasQueried: boolean; busy: boolean; refresh: () => void; openPanel: () => void };
export type XftFilterWorkbenchProps = {
  mode: XftFilterMode;
  fields: XftFilterField[];
  initialValues?: XftFilterValues;
  schemes?: XftFilterScheme[];
  schemesEnabled?: boolean;
  headerLayout?: "standard" | "quick";
  quickFieldKeys?: string[];
  summaryFieldKeys?: string[];
  summarySearchKey?: string;
  onSchemesChange?: (schemes: XftFilterScheme[]) => void;
  onQuery: (values: XftFilterValues) => void | Promise<void>;
  onClear?: () => void;
  toolbarActions?: ReactNode | ((actions: XftFilterWorkbenchActions) => ReactNode);
  headerPrimaryActions?: ReactNode | ((actions: XftFilterWorkbenchActions) => ReactNode);
  summaryToolbarActions?: ReactNode | ((actions: XftFilterWorkbenchActions) => ReactNode);
  renderGroupSchemeTable?: (binding: XftSchemeManagerTableBinding) => ReactNode;
  children: (binding: XftFilterTableBinding) => ReactNode;
};

const cloneValues = (values: XftFilterValues): XftFilterValues => JSON.parse(JSON.stringify(values));
const isEmpty = (value: XftFilterValue) => value == null || value === "" || value === false || (Array.isArray(value) && (value.length === 0 || value.every((item) => !item)));
const sameValues = (a: XftFilterValues, b: XftFilterValues, fields: XftFilterField[]) => {
  const normalize = (values: XftFilterValues) => Object.fromEntries(Object.entries(values).sort(([left], [right]) => left.localeCompare(right)).map(([key, value]) => {
    const field = fields.find((item) => item.key === key);
    return [key, field?.type === "multi-select" && Array.isArray(value) ? [...value].sort() : value];
  }));
  return JSON.stringify(normalize(a)) === JSON.stringify(normalize(b));
};
const valueText = (value: XftFilterValue, field?: XftFilterField) => {
  if (Array.isArray(value)) {
    if (field?.type === "month-range") return value.map((date) => date ? `${date.slice(0, 4)}年${date.slice(5)}月` : "不限").join("～");
    if (field?.type === "date-range") return value.join(" 至 ");
    if (field?.type === "number-range") return value.join("-");
    return value.length > 1 ? `${value[0]}及${value.length - 1}个选项` : value[0] ?? "";
  }
  return typeof value === "boolean" ? "是" : String(value ?? "");
};

type FieldControlProps = { field: XftFilterField; value: XftFilterValue; change: (value: XftFilterValue) => void };
function FieldControl({ field, value, change }: FieldControlProps) {
  if (field.render) return <>{field.render(value, change)}</>;
  if (field.type === "checkbox") return <Checkbox checked={Boolean(value)} onChange={(event) => change(event.target.checked)}>{field.label}</Checkbox>;
  if (field.type === "select") return <Select value={typeof value === "string" ? value || undefined : undefined} options={field.options} placeholder={field.placeholder} allowClear onChange={(next) => change(next ?? "")} />;
  if (field.type === "multi-select") return <Select mode="multiple" maxTagCount="responsive" maxTagPlaceholder={(omitted) => `+${omitted.length} ...`} value={Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : []} options={field.options} placeholder={field.placeholder} showSearch onChange={change} />;
  if (field.type === "month-range" || field.type === "date-range") {
    const pair = Array.isArray(value) ? value : ["", ""];
    const format = field.type === "month-range" ? "YYYY-MM" : "YYYY-MM-DD";
    const changeStart = (date: dayjs.Dayjs | null) => { const start = date?.format(format) ?? ""; change([start, field.autoAdjustRange && pair[1] && start > pair[1] ? start : pair[1]]); };
    const changeEnd = (date: dayjs.Dayjs | null) => { const end = date?.format(format) ?? ""; change([field.autoAdjustRange && pair[0] && end && end < pair[0] ? end : pair[0], end]); };
    return <div className="xft-filter-workbench__range"><DatePicker picker={field.type === "month-range" ? "month" : "date"} format={field.type === "month-range" ? "YYYY年MM月" : "YYYY-MM-DD"} value={pair[0] ? dayjs(pair[0]) : null} onChange={changeStart} /><span>→</span><DatePicker picker={field.type === "month-range" ? "month" : "date"} format={field.type === "month-range" ? "YYYY年MM月" : "YYYY-MM-DD"} value={pair[1] ? dayjs(pair[1]) : null} onChange={changeEnd} /></div>;
  }
  if (field.type === "number-range") {
    const pair = Array.isArray(value) ? value : ["", ""];
    return <div className="xft-filter-workbench__range"><InputNumber value={pair[0] ? Number(pair[0]) : null} onChange={(next) => change([String(next ?? ""), pair[1]])} /><span>至</span><InputNumber value={pair[1] ? Number(pair[1]) : null} onChange={(next) => change([pair[0], String(next ?? "")])} /></div>;
  }
  return <Input value={typeof value === "string" ? value : ""} placeholder={field.placeholder} onChange={(event) => change(event.target.value)} />;
}

function FieldRow({ field, value, change }: FieldControlProps) {
  return <div className={`xft-filter-workbench__field${field.type === "checkbox" ? " is-checkbox" : ""}`}><span>{field.required ? <b>* </b> : null}{field.type === "checkbox" ? "" : field.label}</span><FieldControl field={field} value={value} change={change} /></div>;
}

type ColumnEditorProps = { field: XftFilterField; applied: XftFilterValue; confirm: (value: XftFilterValue) => void; close: () => void };
function ColumnEditor({ field, applied, confirm, close }: ColumnEditorProps) {
  const [draft, setDraft] = useState<XftFilterValue>(applied);
  const [search, setSearch] = useState("");
  useEffect(() => setDraft(applied), [applied]);
  const isMulti = field.type === "multi-select";
  const isDate = field.type === "date-range";
  const options = field.options?.filter((option) => option.label.toLowerCase().includes(search.trim().toLowerCase())) ?? [];
  const selected = Array.isArray(draft) ? draft : [];
  const pair = Array.isArray(draft) ? draft : ["", ""];
  function setQuickDate(days: number) { const end = dayjs(); setDraft([end.subtract(days, "day").format("YYYY-MM-DD"), end.format("YYYY-MM-DD")]); }
  return <div className="xft-filter-workbench__column-editor">{isMulti ? <><label className="xft-filter-workbench__column-search"><SearchOutlined /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="在筛选项中搜索" /></label><div className="xft-filter-workbench__column-options">{options.length ? options.map((option) => <label key={option.value}><input type="checkbox" checked={selected.includes(option.value)} onChange={(event) => setDraft(event.target.checked ? [...selected, option.value] : selected.filter((item) => item !== option.value))} />{option.label}</label>) : <span>没有匹配的选项</span>}</div></> : isDate ? <><DatePicker value={pair[0] ? dayjs(pair[0]) : null} onChange={(date) => setDraft([date?.format("YYYY-MM-DD") ?? "", pair[1]])} placeholder="开始日期" /><DatePicker value={pair[1] ? dayjs(pair[1]) : null} onChange={(date) => setDraft([pair[0], date?.format("YYYY-MM-DD") ?? ""])} placeholder="结束日期" /><div className="xft-filter-workbench__quick-dates">{[["今天", 0], ["近一周", 6], ["近一月", 29], ["近三月", 89], ["近半年", 179], ["近一年", 364]].map(([label, days]) => <button type="button" key={label} onClick={() => setQuickDate(Number(days))}>{label}</button>)}</div></> : <FieldControl field={field} value={draft} change={setDraft} />}<div className="xft-filter-workbench__column-actions"><Button autoInsertSpace={false} onClick={() => setDraft(isMulti ? [] : isDate ? ["", ""] : null)}>重置</Button><Button autoInsertSpace={false} type="primary" onClick={() => { confirm(draft); close(); }}>确定</Button></div></div>;
}

type SchemeManagerPanelProps = {
  mode: XftFilterMode;
  schemes: XftFilterScheme[];
  selectedId: string | null;
  fields: XftFilterField[];
  onSelect: (id: string) => void;
  onAdd: () => void;
  onDelete: (id: string) => void;
  onUpdate: (id: string, change: (scheme: XftFilterScheme) => XftFilterScheme) => void;
  onDefault: (id: string) => void;
  renderGroupSchemeTable?: (binding: XftSchemeManagerTableBinding) => ReactNode;
};
function SchemeManagerPanel({ mode, schemes, selectedId, fields, onSelect, onAdd, onDelete, onUpdate, onDefault, renderGroupSchemeTable }: SchemeManagerPanelProps) {
  const [query, setQuery] = useState("");
  const selected = schemes.find((item) => item.id === selectedId) ?? schemes[0];
  const limit = mode === "header" ? 100 : mode === "realtime-scheme" ? 20 : Infinity;
  if (mode === "group-finance") {
    return renderGroupSchemeTable?.({
      schemes,
      onRename: (id, name) => onUpdate(id, (item) => ({ ...item, name })),
      onDefault,
      onDelete
    }) ?? null;
  }
  const managerFields = fields.filter((field) => field.showInManager !== false);
  const checkboxFields = managerFields.filter((field) => field.type === "checkbox");
  const editorFields = managerFields.filter((field) => field.type !== "checkbox");
  const updateField = (key: string, value: XftFilterValue) => selected && onUpdate(selected.id, (item) => ({ ...item, values: { ...item.values, [key]: value } }));
  return <div className="xft-filter-workbench__manager">
    <aside className="xft-filter-workbench__manager-list">
      <div className="xft-filter-workbench__manager-top"><span>{mode === "realtime-scheme" ? "筛选方案列表" : "方案列表"} {schemes.length}/{limit}</span><button type="button" disabled={schemes.length >= limit} onClick={onAdd}>＋ {mode === "realtime-scheme" ? "添加" : "新增方案"}</button></div>
      <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索方案" prefix={<SearchOutlined />} />
      <div className="xft-filter-workbench__manager-plans">{schemes.filter((item) => item.name.toLowerCase().includes(query.trim().toLowerCase())).map((scheme) => <div key={scheme.id} className={`xft-filter-workbench__manager-plan${selected?.id === scheme.id ? " is-selected" : ""}`}><button type="button" title={scheme.name} onClick={() => onSelect(scheme.id)}>{scheme.name}{scheme.isDefault ? <small>默认</small> : null}</button><button type="button" aria-label={`删除方案：${scheme.name}`} disabled={schemes.length <= 1} onClick={() => onDelete(scheme.id)}><DeleteOutlined /></button></div>)}</div>
    </aside>
    {selected ? <div className="xft-filter-workbench__manager-editor">
      <div className="xft-filter-workbench__manager-editor-head">{mode === "realtime-scheme" ? "设置" : "方案设置"}<label><input type="checkbox" checked={Boolean(selected.isDefault)} onChange={() => onDefault(selected.id)} />设为默认</label></div>
      <div className="xft-filter-workbench__manager-editor-body">
        {mode === "header" ? <label className="xft-filter-workbench__manager-name">方案名称<Input value={selected.name} maxLength={12} onChange={(event) => onUpdate(selected.id, (item) => ({ ...item, name: event.target.value }))} /></label> : <div className="xft-filter-workbench__manager-name"><label htmlFor="xft-manager-scheme-name"><b>* </b>筛选方案名称</label><Input id="xft-manager-scheme-name" value={selected.name} maxLength={12} onChange={(event) => onUpdate(selected.id, (item) => ({ ...item, name: event.target.value }))} /></div>}
        {mode === "header" ? <div className="xft-filter-workbench__manager-rules">{Object.keys(selected.values).filter((key) => fields.some((field) => field.key === key)).map((key) => { const field = fields.find((item) => item.key === key)!; return <div className="xft-filter-workbench__manager-rule" key={key}><div><strong>{field.label}</strong><button type="button" aria-label={`删除筛选项：${field.label}`} onClick={() => onUpdate(selected.id, (item) => { const values = { ...item.values }; delete values[key]; return { ...item, values }; })}><DeleteOutlined /></button></div><FieldControl field={field} value={selected.values[key]} change={(value) => updateField(key, value)} /></div>; })}<Select placeholder="添加筛选项" value={undefined} options={fields.filter((field) => !(field.key in selected.values)).map((field) => ({ label: field.label, value: field.key }))} onChange={(key) => onUpdate(selected.id, (item) => ({ ...item, values: { ...item.values, [key]: fields.find((field) => field.key === key)?.type === "multi-select" ? [] : null } }))} /></div> : <><div className="xft-filter-workbench__manager-fields">{editorFields.map((field) => <FieldRow key={field.key} field={field} value={selected.values[field.key]} change={(value) => updateField(field.key, value)} />)}</div>{checkboxFields.length ? <div className="xft-filter-workbench__manager-other"><span>其他</span><div>{checkboxFields.map((field) => <FieldControl key={field.key} field={field} value={selected.values[field.key]} change={(value) => updateField(field.key, value)} />)}</div></div> : null}</>}
      </div>
    </div> : null}
  </div>;
}

export function XftFilterWorkbench({ mode, fields, initialValues, schemes, schemesEnabled, headerLayout = "standard", quickFieldKeys, summaryFieldKeys, summarySearchKey, onSchemesChange, onQuery, onClear, toolbarActions, headerPrimaryActions, summaryToolbarActions, renderGroupSchemeTable, children }: XftFilterWorkbenchProps) {
  const [applied, setApplied] = useState<XftFilterValues>(() => cloneValues(initialValues ?? {}));
  const [draft, setDraft] = useState<XftFilterValues>(() => cloneValues(initialValues ?? {}));
  const [localSchemes, setSchemes] = useState<XftFilterScheme[]>(schemes ?? []);
  const [selectedSchemeId, setSelectedSchemeId] = useState<string | null>(schemes?.find((item) => item.isDefault)?.id ?? null);
  const [panelOpen, setPanelOpen] = useState(mode === "group-finance");
  const [hasQueried, setHasQueried] = useState(false);
  const [busy, setBusy] = useState(false);
  const [queryProgress, setQueryProgress] = useState(0);
  const [expanded, setExpanded] = useState(false);
  const [conditionsOverflow, setConditionsOverflow] = useState(false);
  const [appliedSchemeLabel, setAppliedSchemeLabel] = useState<string | null>(null);
  const [saveOpen, setSaveOpen] = useState(false);
  const [schemeName, setSchemeName] = useState("");
  const [saveAsDefault, setSaveAsDefault] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [saveSource, setSaveSource] = useState<"applied" | "draft">("applied");
  const [manageOpen, setManageOpen] = useState(false);
  const [manageError, setManageError] = useState("");
  const [manageDraft, setManageDraft] = useState<XftFilterScheme[]>([]);
  const [manageSelectedId, setManageSelectedId] = useState<string | null>(null);
  const [toast, setToast] = useState("");
  const [schemeOverflow, setSchemeOverflow] = useState(false);
  const [schemeListElement, setSchemeListElement] = useState<HTMLDivElement | null>(null);
  const [schemeSearchOpen, setSchemeSearchOpen] = useState(false);
  const [schemeQuery, setSchemeQuery] = useState("");
  const [quickWidth, setQuickWidth] = useState(0);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const queryProgressTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const busyRef = useRef(false);
  const pendingQuickRef = useRef<XftFilterValues | null>(null);
  const draftRevisionRef = useRef(0);
  const panelDialogOpenRef = useRef(false);
  const schemeListRef = useRef<HTMLDivElement>(null);
  const quickListRef = useRef<HTMLDivElement>(null);
  const setSchemeListRef = useCallback((element: HTMLDivElement | null) => { schemeListRef.current = element; setSchemeListElement(element); }, []);
  const summaryRef = useRef<HTMLDivElement>(null);
  const chipsRef = useRef<HTMLDivElement>(null);
  useEffect(() => { if (schemes) setSchemes(schemes); }, [schemes]);
  const fieldByKey = new Map(fields.map((field) => [field.key, field]));
  const quickKeys = mode === "quick" ? quickFieldKeys ?? fields.map((field) => field.key) : quickFieldKeys ?? [];
  const quickFields = quickKeys.map((key) => fieldByKey.get(key)).filter((field): field is XftFilterField => Boolean(field));
  useLayoutEffect(() => {
    const element = quickListRef.current;
    if (!element) return;
    const measure = () => setQuickWidth(element.clientWidth);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => observer.disconnect();
  }, [mode, headerLayout, quickKeys.join("|")]);
  const quickFieldWidth = (field: XftFilterField) => field.type === "date-range" || field.type === "month-range" ? 248 : field.type === "search" ? 220 : field.type === "select" || field.type === "multi-select" ? 150 : 180;
  let visibleQuickCount = quickFields.length;
  if (quickWidth > 0 && quickFields.reduce((total, field, index) => total + quickFieldWidth(field) + (index ? 8 : 0), 0) > quickWidth) {
    const available = Math.max(0, quickWidth - 92);
    let used = 0;
    visibleQuickCount = 0;
    for (const field of quickFields) {
      const next = used + quickFieldWidth(field) + (visibleQuickCount ? 8 : 0);
      if (next > available) break;
      used = next;
      visibleQuickCount += 1;
    }
  }
  const conditionKeys = summaryFieldKeys ?? (mode === "header" ? fields.map((field) => field.key).filter((key) => !quickKeys.includes(key) && key !== summarySearchKey) : null);
  const entries = Object.entries(applied).filter(([key, value]) => (!conditionKeys || conditionKeys.includes(key)) && !isEmpty(value));
  const summaryItems = entries.flatMap(([key, value]) => {
    const field = fieldByKey.get(key);
    if (field?.summaryItems) return field.summaryItems(value).map((item) => ({ ...item, key, remove: () => removeCondition(key, item.nextValue) }));
    const summaryText = field?.summarize?.(value) ?? valueText(value, field);
    const label = mode === "group-finance" && field?.type === "checkbox" ? "其他" : field?.label ?? key;
    const text = mode === "group-finance" && field?.type === "checkbox" ? field.label : summaryText;
    const full = Array.isArray(value) && field?.type === "multi-select" ? value.join("、") : summaryText;
    return [{ id: key, key, text: `${label}：${text}`, title: `${label}：${full}`, remove: () => removeCondition(key, null) }];
  });
  const showSummary = mode === "header" || mode === "realtime-scheme" || (mode === "group-finance" && hasQueried);
  const canUseSchemes = mode !== "header" || (schemesEnabled ?? Boolean(schemes?.length));
  const showSchemeRow = canUseSchemes && (mode === "header" || mode === "realtime-scheme") && localSchemes.length > 0;
  useLayoutEffect(() => {
    const summaryElement = summaryRef.current;
    const chipsElement = chipsRef.current;
    if (!summaryElement || !chipsElement) return;
    const measure = () => {
      if (expanded) return;
      setConditionsOverflow(chipsElement.scrollHeight > chipsElement.clientHeight + 1);
    };
    const frame = requestAnimationFrame(measure);
    const observer = new ResizeObserver(measure);
    observer.observe(summaryElement);
    observer.observe(chipsElement);
    return () => { cancelAnimationFrame(frame); observer.disconnect(); };
  }, [expanded, applied, showSummary]);
  useEffect(() => {
    const onResize = () => setExpanded(false);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  useEffect(() => () => { if (toastTimerRef.current) clearTimeout(toastTimerRef.current); }, []);
  useEffect(() => {
    if (mode !== "group-finance" || !busy) return;
    const started = performance.now();
    setQueryProgress(0);
    const timer = setInterval(() => setQueryProgress(Math.min(96, Math.round((performance.now() - started) / 4300 * 100))), 90);
    queryProgressTimerRef.current = timer;
    return () => { clearInterval(timer); if (queryProgressTimerRef.current === timer) queryProgressTimerRef.current = null; };
  }, [busy, mode]);
  useLayoutEffect(() => {
    const list = schemeListElement;
    if (!list) return;
    const measure = () => setSchemeOverflow(list.scrollWidth > list.clientWidth + 1);
    const frame = requestAnimationFrame(measure);
    const observer = new ResizeObserver(measure);
    observer.observe(list);
    window.addEventListener("resize", measure);
    return () => { cancelAnimationFrame(frame); observer.disconnect(); window.removeEventListener("resize", measure); };
  }, [localSchemes, mode, panelOpen, schemeListElement]);
  function showToast(message: string) { setToast(message); if (toastTimerRef.current) clearTimeout(toastTimerRef.current); toastTimerRef.current = setTimeout(() => setToast(""), 2000); }

  async function apply(next: XftFilterValues, schemeId: string | null = null, schemeLabel: string | null = null, successMessage?: string, queueIfBusy = false) {
    if (busyRef.current) { if (queueIfBusy) pendingQuickRef.current = cloneValues(next); return; }
    busyRef.current = true;
    setBusy(true);
    const draftRevision = draftRevisionRef.current;
    if (mode === "group-finance") setPanelOpen(false);
    try {
      await onQuery(cloneValues(next));
      setApplied(cloneValues(next));
      if (draftRevisionRef.current === draftRevision && !pendingQuickRef.current) setDraft(cloneValues(next));
      setSelectedSchemeId(schemeId);
      if (mode === "group-finance") setAppliedSchemeLabel(schemeLabel ?? "自定义筛选");
      setHasQueried(true);
      setPanelOpen(false);
      if (successMessage) showToast(successMessage);
      if (mode === "group-finance") {
        if (queryProgressTimerRef.current) clearInterval(queryProgressTimerRef.current);
        queryProgressTimerRef.current = null;
        setQueryProgress(100);
        await new Promise((resolve) => setTimeout(resolve, 180));
      }
    } catch { showToast("查询失败，请稍后重试"); }
    finally {
      busyRef.current = false;
      setBusy(false);
      const pending = pendingQuickRef.current;
      pendingQuickRef.current = null;
      if (pending) void apply(pending, null, null, undefined, true);
    }
  }
  function changeDraft(key: string, value: XftFilterValue) { draftRevisionRef.current += 1; setDraft((current) => ({ ...current, [key]: value })); if (mode === "realtime-scheme") setSelectedSchemeId(null); }
  function queryQuick(key: string, value: XftFilterValue) {
    const next = { ...draft, [key]: value };
    draftRevisionRef.current += 1;
    setDraft(next);
    void apply(next, null, null, undefined, true);
  }
  function validate(values: XftFilterValues) {
    const missing = fields.find((field) => {
      if (!field.required) return false;
      const value = values[field.key];
      if (["month-range", "date-range", "number-range"].includes(field.type ?? "")) return !Array.isArray(value) || !value[0] || !value[1];
      return isEmpty(value);
    });
    if (missing) {
      const message = mode === "group-finance" ? "请完善查询主账套、会计期间和账套范围"
        : missing.type === "month-range" ? "请选择会计期间"
          : missing.type === "number-range" && mode === "realtime-scheme" ? "请检查科目级次范围"
            : `请完善${missing.label}`;
      showToast(message); return false;
    }
    for (const field of fields) {
      const value = values[field.key];
      if (!Array.isArray(value) || !value[0] || !value[1]) continue;
      if ((field.type === "month-range" || field.type === "date-range") && value[0] > value[1]) {
        showToast(mode === "group-finance" ? "开始会计期间不能晚于结束会计期间" : "结束会计期间不能早于开始会计期间"); return false;
      }
      if (field.type === "number-range" && (!Number.isFinite(Number(value[0])) || !Number.isFinite(Number(value[1])) || Number(value[0]) > Number(value[1]))) {
        showToast(mode === "realtime-scheme" ? "请检查科目级次范围" : "请填写有效的科目级次范围"); return false;
      }
    }
    return true;
  }
  async function queryDraft() {
    if (!validate(draft)) return;
    const selected = localSchemes.find((item) => item.id === selectedSchemeId);
    const matches = Boolean(selected && sameValues(draft, selected.values, fields));
    if (mode === "group-finance") await apply(draft, selectedSchemeId, selected ? `${selected.name}${matches ? "" : "（已调整）"}` : "自定义筛选", "查询完成");
    else await apply(draft, matches ? selectedSchemeId : null, null, mode === "realtime-scheme" ? "查询完成，当前条件已更新" : mode === "precondition" ? "查询完成" : undefined);
  }
  function selectScheme(scheme: XftFilterScheme) {
    if (mode === "group-finance") { setDraft(cloneValues(scheme.values)); setSelectedSchemeId(scheme.id); return; }
    void apply(scheme.values, scheme.id, null, "已切换方案并实时更新结果");
  }
  function openSave(source: "applied" | "draft") { if (mode === "group-finance") panelDialogOpenRef.current = true; setSaveSource(source); setSchemeName(""); setSaveAsDefault(false); setSaveError(""); setSaveOpen(true); }
  async function saveScheme() {
    const name = schemeName.trim();
    const limit = mode === "header" ? 100 : mode === "realtime-scheme" ? 20 : Infinity;
    if (!name) { setSaveError("请输入方案名称"); return; }
    if (name.length > 12) { setSaveError("方案名称最多 12 个字"); return; }
    if (localSchemes.some((item) => item.name === name)) { setSaveError("方案名称已存在"); return; }
    if (localSchemes.length >= limit) { setSaveError(`常用筛选方案已达${limit}个上限`); return; }
    const values = saveSource === "draft" ? draft : applied;
    const next = [...localSchemes.map((item) => saveAsDefault ? { ...item, isDefault: false } : item), { id: `scheme-${Date.now()}`, name, values: cloneValues(values), isDefault: saveAsDefault }];
    setSchemes(next); onSchemesChange?.(next); setSelectedSchemeId(next[next.length - 1].id); setSaveOpen(false); setSchemeName("");
    showToast("方案保存成功");
    if (mode === "realtime-scheme" || mode === "header") await apply(values, next[next.length - 1].id, null, mode === "realtime-scheme" ? "保存成功，查询结果已更新" : undefined);
  }
  function openManager() { if (mode === "group-finance") panelDialogOpenRef.current = true; setManageDraft(localSchemes.map((item) => ({ ...item, values: cloneValues(item.values) }))); setManageSelectedId(selectedSchemeId ?? localSchemes[0]?.id ?? null); setManageError(""); setManageOpen(true); }
  function updateManaged(id: string, change: (scheme: XftFilterScheme) => XftFilterScheme) { setManageDraft((current) => current.map((item) => item.id === id ? change(item) : item)); setManageError(""); }
  function addManaged() {
    const limit = mode === "header" ? 100 : mode === "realtime-scheme" ? 20 : Infinity;
    if (manageDraft.length >= limit) { showToast(`常用筛选方案已达${limit}个上限`); return; }
    const id = `scheme-${Date.now()}`;
    setManageDraft((current) => [...current, { id, name: `新方案${current.length + 1}`, values: cloneValues(initialValues ?? {}) }]);
    setManageSelectedId(id);
  }
  function deleteManaged(id: string) {
    if (manageDraft.length <= 1) { showToast("至少保留一个方案"); return; }
    const next = manageDraft.filter((item) => item.id !== id);
    setManageDraft(next);
    if (manageSelectedId === id) setManageSelectedId(next.find((item) => item.isDefault)?.id ?? next[0].id);
  }
  function setManagedDefault(id: string) { setManageDraft((current) => current.map((item) => ({ ...item, isDefault: item.id === id }))); }
  function saveManager() {
    const maxNameLength = mode === "group-finance" ? 30 : 12;
    if (!manageDraft.length) { setManageError("至少保留一个方案"); return; }
    if (manageDraft.some((item) => !item.name.trim())) { setManageError("筛选方案名称不能为空"); return; }
    if (manageDraft.some((item) => item.name.trim().length > maxNameLength)) { setManageError(`方案名称最多${maxNameLength}个字`); return; }
    if (new Set(manageDraft.map((item) => item.name.trim())).size !== manageDraft.length) { setManageError("筛选方案名称不能重复"); return; }
    setSchemes(manageDraft); onSchemesChange?.(manageDraft); setManageOpen(false);
    const active = manageDraft.find((item) => item.id === selectedSchemeId) ?? manageDraft.find((item) => item.isDefault) ?? manageDraft[0];
    if (mode === "group-finance") { setDraft(cloneValues(active.values)); setSelectedSchemeId(active.id); showToast("常用筛选方案已保存"); }
    else void apply(active.values, active.id);
  }
  function removeCondition(key: string, nextValue: XftFilterValue) { void apply({ ...applied, [key]: nextValue }, null, null, mode === "realtime-scheme" ? "条件已移除，结果已实时更新" : undefined); }
  function clearConditions() {
    if (mode === "realtime-scheme") { setApplied({}); setDraft({}); setSelectedSchemeId(null); setHasQueried(false); onClear?.(); showToast("当前筛选条件已清空"); }
    else if (mode === "header") {
      const next = { ...applied };
      for (const key of conditionKeys ?? Object.keys(applied)) delete next[key];
      void apply(next);
    }
    else void apply({});
  }
  function resetDraft() {
    setDraft(cloneValues(initialValues ?? {}));
    if (mode === "realtime-scheme") { setSelectedSchemeId(null); showToast("已重置筛选表单"); }
    if (mode === "precondition") showToast("已重置筛选条件");
  }
  function clearGroupDraft() {
    const keep: XftFilterValues = {};
    for (const field of fields) if (field.key === "ledger" || field.type === "month-range") keep[field.key] = draft[field.key];
    setDraft(keep);
    setSelectedSchemeId(null);
  }
  function saveCurrentScheme() {
    const current = localSchemes.find((item) => item.id === selectedSchemeId);
    if (!current) { openSave("draft"); return; }
    const next = localSchemes.map((item) => item.id === current.id ? { ...item, values: cloneValues(draft) } : item);
    setSchemes(next); onSchemesChange?.(next);
    showToast("方案保存成功");
  }
  function refresh() {
    if (busy) return;
    if (!hasQueried && (mode === "header" || mode === "quick")) { void apply(applied); return; }
    if (!hasQueried) { setPanelOpen(true); if (mode === "realtime-scheme") showToast("请先设置筛选条件"); return; }
    void apply(applied, selectedSchemeId, appliedSchemeLabel, mode === "group-finance" ? "查询完成" : "查询完成，当前条件已更新");
  }
  const actions: XftFilterWorkbenchActions = { applied, hasQueried, busy, refresh, openPanel: () => setPanelOpen(true) };
  const actionContent = typeof toolbarActions === "function" ? toolbarActions(actions) : toolbarActions;
  const topActionContent = typeof headerPrimaryActions === "function" ? headerPrimaryActions(actions) : headerPrimaryActions;
  const summaryActionContent = typeof summaryToolbarActions === "function" ? summaryToolbarActions(actions) : summaryToolbarActions;
  const binding: XftFilterTableBinding = {
    filterValues: applied,
    busy,
    renderColumnFilter: (key, close) => {
      const field = fieldByKey.get(key);
      return field ? <ColumnEditor key={key} field={field} applied={applied[key]} confirm={(value) => { void apply({ ...applied, [key]: value }); }} close={close} /> : null;
    }
  };
  const schemeRow = <div className="xft-filter-workbench__schemes"><span>常用筛选方案</span><div className="xft-filter-workbench__scheme-list" ref={setSchemeListRef}>{localSchemes.map((scheme) => <button key={scheme.id} type="button" className={`xft-filter-workbench__scheme${selectedSchemeId === scheme.id ? " is-selected" : ""}`} title={scheme.name} onClick={() => selectScheme(scheme)}>{scheme.name}</button>)}</div>{schemeOverflow ? <div className="xft-filter-workbench__scheme-nav"><button type="button" aria-label="向左查看方案" onClick={() => schemeListRef.current?.scrollBy({ left: -180, behavior: "smooth" })}><LeftOutlined /></button><button type="button" aria-label="向右查看方案" onClick={() => schemeListRef.current?.scrollBy({ left: 180, behavior: "smooth" })}><RightOutlined /></button>{mode !== "group-finance" ? <Popover trigger="click" open={schemeSearchOpen} onOpenChange={setSchemeSearchOpen} content={<div className="xft-filter-workbench__scheme-search"><Input value={schemeQuery} onChange={(event) => setSchemeQuery(event.target.value)} placeholder="搜索方案" />{localSchemes.filter((item) => item.name.toLowerCase().includes(schemeQuery.trim().toLowerCase())).length ? localSchemes.filter((item) => item.name.toLowerCase().includes(schemeQuery.trim().toLowerCase())).map((item) => <button key={item.id} type="button" onClick={() => { selectScheme(item); setSchemeSearchOpen(false); setSchemeQuery(""); }}>{item.name}</button>) : <div className="xft-filter-workbench__scheme-search-empty">没有匹配的方案</div>}</div>}><button type="button" aria-label="搜索方案"><SearchOutlined /></button></Popover> : null}</div> : null}<button className="xft-filter-workbench__icon" type="button" aria-label="常用筛选方案设置" onClick={openManager}><SettingOutlined /></button></div>;
  const summarySearchField = mode === "header" && headerLayout === "standard" && summarySearchKey ? fieldByKey.get(summarySearchKey) : null;
  const summary = <div ref={summaryRef} className={"xft-filter-workbench__summary" + (expanded ? " is-expanded" : "")}>
    <div className="xft-filter-workbench__summary-main">
      <span>当前筛选条件</span>
      <div ref={chipsRef} className={"xft-filter-workbench__chips" + (expanded ? " is-expanded" : "")}>
        {summaryItems.length ? summaryItems.map((item) => <Tooltip key={item.key + "-" + item.id} title={item.title ?? item.text}>
          <span className="xft-filter-workbench__chip"><span className="xft-filter-workbench__chip-text">{item.text}</span>
            {mode !== "group-finance" ? <button type="button" aria-label={"移除" + item.text} onClick={item.remove}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg></button> : null}
          </span>
        </Tooltip>) : <span className="xft-filter-workbench__chip">全部</span>}
      </div>
      {(conditionsOverflow || expanded) ? <button className="xft-filter-workbench__text-action" type="button" aria-expanded={expanded} onClick={() => setExpanded((current) => !current)}>
        {expanded ? "收起条件" : "展开所有条件"}{expanded ? <UpOutlined /> : <DownOutlined />}
      </button> : null}
      {summaryItems.length > 0 && mode !== "group-finance" ? <div className="xft-filter-workbench__summary-actions">
        {canUseSchemes ? <button className="xft-filter-workbench__icon" type="button" aria-label="另存为常用筛选方案" onClick={() => openSave("applied")}><SaveOutlined /></button> : null}
        <button className="xft-filter-workbench__icon" type="button" aria-label="清空当前筛选条件" onClick={clearConditions}><DeleteOutlined /></button>
      </div> : null}
    </div>
    {summarySearchField || summaryActionContent ? <div className="xft-filter-workbench__summary-utilities">
      {summarySearchField ? <Input.Search aria-label={summarySearchField.label} placeholder={summarySearchField.placeholder ?? summarySearchField.label} value={typeof draft[summarySearchField.key] === "string" ? draft[summarySearchField.key] as string : ""} onChange={(event) => changeDraft(summarySearchField.key, event.target.value)} onSearch={(value) => queryQuick(summarySearchField.key, value)} /> : null}
      {summaryActionContent}
    </div> : null}
  </div>;
  const editableFields = fields.filter((field) => field.type !== "checkbox");
  const checkboxFields = fields.filter((field) => field.type === "checkbox");
  const panelCheckboxFields = checkboxFields.filter((field) => field.showInPanel !== false);
  const form = <div className={`xft-filter-workbench__form xft-filter-workbench__form--${mode}`}>{mode === "group-finance" && localSchemes.length > 0 ? <div className="xft-filter-workbench__panel-head">{schemeRow}</div> : null}<div className="xft-filter-workbench__fields">{editableFields.map((field) => <FieldRow key={field.key} field={field} value={draft[field.key]} change={(value) => changeDraft(field.key, value)} />)}{panelCheckboxFields.length ? <div className="xft-filter-workbench__options">{mode === "group-finance" || mode === "realtime-scheme" ? <span>其他</span> : null}<div>{panelCheckboxFields.map((field) => <FieldControl key={field.key} field={field} value={draft[field.key]} change={(value) => changeDraft(field.key, value)} />)}</div></div> : null}</div><div className="xft-filter-workbench__form-actions">{mode === "group-finance" ? <><Button autoInsertSpace={false} disabled={busy} onClick={clearGroupDraft}>清空</Button><Button autoInsertSpace={false} disabled={busy} onClick={saveCurrentScheme}>保存方案</Button><Button autoInsertSpace={false} disabled={busy} onClick={() => openSave("draft")}>另存为新方案</Button></> : <Button autoInsertSpace={false} onClick={resetDraft}>重置</Button>}{mode === "realtime-scheme" ? <Button autoInsertSpace={false} disabled={busy} onClick={() => openSave("draft")}>保存方案并查询</Button> : null}<Tooltip title={mode === "group-finance" && busy ? "正在查询，请稍候" : ""}><Button autoInsertSpace={false} type="primary" loading={busy} disabled={busy} onClick={() => void queryDraft()}>{busy ? (mode === "group-finance" ? "查询中" : "查询中…") : "查询"}</Button></Tooltip></div></div>;
  const periodField = fields.find((field) => field.type === "month-range");
  const renderQuickControl = (field: XftFilterField, inOverflow = false) => <div className={"xft-filter-workbench__quick-field xft-filter-workbench__quick-field--" + (field.type ?? "text")} key={field.key}>
    {inOverflow ? <span className="xft-filter-workbench__quick-field-label">{field.label}</span> : null}
    {field.type === "search" ? <Input.Search aria-label={field.label} placeholder={field.placeholder ?? field.label} value={typeof draft[field.key] === "string" ? draft[field.key] as string : ""} onChange={(event) => changeDraft(field.key, event.target.value)} onSearch={(value) => queryQuick(field.key, value)} /> :
      <FieldControl field={field} value={draft[field.key]} change={(value) => queryQuick(field.key, value)} />}
  </div>;
  const quickControls = quickFields.slice(0, visibleQuickCount).map((field) => renderQuickControl(field));
  const hiddenQuickFields = quickFields.slice(visibleQuickCount);
  const quickToolbar = <div className="xft-filter-workbench__toolbar xft-filter-workbench__toolbar--inline">
    {quickFields.length ? <div className="xft-filter-workbench__quick-fields" ref={quickListRef}>
      {quickControls}
      {hiddenQuickFields.length ? <Popover placement="bottomLeft" trigger="click" overlayClassName="xft-filter-workbench__quick-overflow-popover" content={<div className="xft-filter-workbench__quick-overflow">{hiddenQuickFields.map((field) => renderQuickControl(field, true))}</div>}>
        <Button className="xft-filter-workbench__quick-more" type="link" icon={<DownOutlined />} iconPosition="end">更多筛选</Button>
      </Popover> : null}
    </div> : null}
    {actionContent ? <div className="xft-filter-workbench__toolbar-actions">{actionContent}</div> : null}
  </div>;
  const toolbar = mode === "precondition" ? <div className="xft-filter-workbench__toolbar xft-filter-workbench__toolbar--inline">
    <div className="xft-filter-workbench__quick">
      {periodField ? <FieldControl field={periodField} value={draft[periodField.key]} change={(value) => changeDraft(periodField.key, value)} /> : null}
      <Popover placement="bottomLeft" align={{ offset: [0, 5] }} trigger="click" open={panelOpen} onOpenChange={setPanelOpen} overlayClassName="xft-filter-workbench__popover xft-filter-workbench__popover--precondition" content={form}>
        <button className="xft-filter-workbench__quick-button" type="button" aria-expanded={panelOpen}>筛选</button>
      </Popover>
    </div>
    {actionContent ? <div className="xft-filter-workbench__toolbar-actions">{actionContent}</div> : null}
  </div> : mode === "group-finance" ? <div className="xft-filter-workbench__toolbar xft-filter-workbench__toolbar--inline">
    <Popover placement="bottomLeft" align={{ offset: [0, 4] }} trigger="click" open={panelOpen} onOpenChange={(open) => { if (!open && panelDialogOpenRef.current) return; setPanelOpen(open); }} overlayClassName="xft-filter-workbench__popover xft-filter-workbench__popover--group-finance" content={form}>
      <Button autoInsertSpace={false} disabled={busy} className="xft-filter-workbench__filter-button" icon={<FilterOutlined />} aria-expanded={panelOpen}><span>{appliedSchemeLabel ? "筛选 · " + appliedSchemeLabel : "筛选"}</span></Button>
    </Popover>
    {actionContent ? <div className="xft-filter-workbench__toolbar-actions">{actionContent}</div> : null}
  </div> : mode === "quick" ? quickToolbar : null;
  return <section className={"xft-filter-workbench xft-filter-workbench--" + mode + (mode === "group-finance" && hasQueried ? " is-queried" : "")} data-xft-workspace-layout="managed" data-xft-scroll-owner="template">
    {mode === "realtime-scheme" ? <div className="xft-filter-workbench__card">
      <div className="xft-filter-workbench__card-main xft-filter-workbench__toolbar--inline">
        <div className="xft-filter-workbench__card-leading">
          {showSchemeRow ? schemeRow : null}
          <Popover placement="bottomLeft" align={{ offset: [0, 6] }} trigger="click" open={panelOpen} onOpenChange={(open) => { if (open) setDraft(cloneValues(applied)); setPanelOpen(open); }} overlayClassName="xft-filter-workbench__popover xft-filter-workbench__popover--realtime-scheme" content={form}>
            <button className="xft-filter-workbench__filter-link" type="button" aria-expanded={panelOpen}><FilterOutlined />筛选</button>
          </Popover>
        </div>
        {actionContent ? <div className="xft-filter-workbench__toolbar-actions">{actionContent}</div> : null}
      </div>
      {summary}
    </div> : null}
    {mode === "header" ? <>
      {headerLayout === "quick" ? quickToolbar : topActionContent ? <div className="xft-filter-workbench__header-actions">{topActionContent}</div> : null}
      {showSchemeRow ? schemeRow : null}
      {summary}
    </> : null}
    {toolbar}
    {mode === "group-finance" && showSummary ? summary : null}
    <div className="xft-filter-workbench__results">{children(binding)}{mode === "group-finance" ? <div className={`xft-filter-workbench__progress${busy ? " is-visible" : ""}`} role="progressbar" aria-label="查询进度" aria-valuemin={0} aria-valuemax={100} aria-valuenow={queryProgress}><div className="xft-filter-workbench__progress-content"><span>正在查询</span><span className="xft-filter-workbench__progress-percent">{queryProgress}%</span><div className="xft-filter-workbench__progress-track"><div className="xft-filter-workbench__progress-bar" style={{ width: `${queryProgress}%` }} /></div></div></div> : null}</div>
    <Modal title={mode === "group-finance" ? "另存为新方案" : mode === "realtime-scheme" && saveSource === "draft" ? "新增筛选方案" : "另存为常用筛选方案"} open={saveOpen} onOk={() => void saveScheme()} onCancel={() => setSaveOpen(false)} afterClose={() => { panelDialogOpenRef.current = false; }} cancelButtonProps={{ autoInsertSpace: false }} okButtonProps={{ autoInsertSpace: false }} okText={mode === "realtime-scheme" ? "保存并查询" : "保存"} width={mode === "realtime-scheme" ? 480 : 420} className="xft-filter-workbench__save-modal" zIndex={1200} cancelText="取消"><label>筛选方案名称<Input value={schemeName} maxLength={12} placeholder="名称最多 12 个字，且不能与现有方案重复" onChange={(event) => { setSchemeName(event.target.value); setSaveError(""); }} /></label><label className="xft-filter-workbench__save-default"><input type="checkbox" checked={saveAsDefault} onChange={(event) => setSaveAsDefault(event.target.checked)} />设为默认</label>{saveError ? <div className="xft-filter-workbench__save-error" role="alert">{saveError}</div> : null}</Modal>
    <Modal title={mode === "group-finance" ? "常用筛选方案设置" : "常用筛选方案管理"} open={manageOpen} onOk={saveManager} onCancel={() => setManageOpen(false)} afterClose={() => { panelDialogOpenRef.current = false; }} width={mode === "group-finance" ? 480 : mode === "header" ? 740 : 880} okText="保存" cancelText="取消" okButtonProps={{ autoInsertSpace: false }} cancelButtonProps={{ autoInsertSpace: false }} zIndex={1200} className={`xft-filter-workbench__manager-modal xft-filter-workbench__manager-modal--${mode}`}><SchemeManagerPanel mode={mode} schemes={manageDraft} selectedId={manageSelectedId} fields={fields} onSelect={(id) => { setManageSelectedId(id); setManageError(""); }} onAdd={addManaged} onDelete={deleteManaged} onUpdate={updateManaged} onDefault={(id) => { setManagedDefault(id); setManageError(""); }} renderGroupSchemeTable={renderGroupSchemeTable} />{manageError ? <div className="xft-filter-workbench__manager-error" role="alert">{manageError}</div> : null}</Modal>
    <div className={`xft-filter-workbench__toast${toast ? " is-visible" : ""}`} role="status" aria-live="polite">{toast}</div>
  </section>;
}
