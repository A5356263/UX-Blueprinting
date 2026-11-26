import React, { useEffect, useRef, useState } from "react";
import type { Dayjs } from "dayjs";
import { Button, DatePicker, Input, Select, Tooltip } from "antd";
import { DownOutlined } from "@ant-design/icons";
import type { XftFilterBarField, XftFilterBarValue, XftFilterBarValues } from "./XftFilterBar.model";
import "./XftFilterBar.css";

export type XftFilterBarProps = {
  fields: XftFilterBarField[];
  value: XftFilterBarValues;
  defaultValue: XftFilterBarValues;
  onChange: (next: XftFilterBarValues) => void;
  onQuery: (value: XftFilterBarValues) => void;
  onReset?: (value: XftFilterBarValues) => void;
};

type XftFilterLabelProps = { label: string };

function XftFilterLabel({ label }: XftFilterLabelProps) {
  const labelRef = useRef<HTMLSpanElement>(null);
  const [overflowed, setOverflowed] = useState(false);

  useEffect(() => {
    const element = labelRef.current;
    if (!element) return;
    const updateOverflow = () => setOverflowed(element.scrollWidth > element.clientWidth);
    updateOverflow();
    const observer = new ResizeObserver(updateOverflow);
    observer.observe(element);
    return () => observer.disconnect();
  }, [label]);

  return <Tooltip title={overflowed ? label : undefined}><span ref={labelRef}>{label}</span></Tooltip>;
}

export function XftFilterBar({ fields, value, defaultValue, onChange, onQuery, onReset }: XftFilterBarProps) {
  const [expanded, setExpanded] = useState(false);
  const hasMoreFilters = fields.length > 3;

  function updateValue(key: string, next: XftFilterBarValue) {
    onChange({ ...value, [key]: next });
  }

  function renderControl(field: XftFilterBarField) {
    const fieldValue = value[field.key];
    if (field.type === "select") {
      return <Select value={typeof fieldValue === "string" ? fieldValue : undefined} placeholder={field.placeholder} options={field.options} disabled={field.disabled} onChange={(next) => updateValue(field.key, next)} />;
    }
    if (field.type === "date") {
      return <DatePicker value={(fieldValue as Dayjs | null | undefined) ?? null} placeholder={field.placeholder} disabled={field.disabled} onChange={(next) => updateValue(field.key, next)} />;
    }
    if (field.type === "range") {
      return <DatePicker.RangePicker value={(fieldValue as [Dayjs | null, Dayjs | null] | undefined) ?? null} placeholder={field.placeholder ? [field.placeholder, field.placeholder] : undefined} disabled={field.disabled} onChange={(next) => updateValue(field.key, next)} />;
    }
    return <Input value={typeof fieldValue === "string" ? fieldValue : ""} placeholder={field.placeholder} disabled={field.disabled} onChange={(event) => updateValue(field.key, event.target.value)} />;
  }

  const visibleFields = hasMoreFilters && !expanded ? fields.slice(0, 3) : fields;
  const controls = <>
    <Button type="primary" ghost onClick={() => onQuery(value)}>查询</Button>
    <Button onClick={() => { onChange(defaultValue); onReset?.(defaultValue); }}>重置</Button>
    {hasMoreFilters ? <Button className="xft-filter-bar__toggle" type="link" icon={<DownOutlined rotate={expanded ? 180 : 0} />} iconPosition="end" onClick={() => setExpanded((current) => !current)}>{expanded ? "收起" : "更多筛选"}</Button> : null}
  </>;

  return <section className="xft-filter-bar">
    <div className="xft-filter-bar__grid" aria-label="筛选条件">
      {visibleFields.map((field) => <label className="xft-filter-bar__field" key={field.key}><XftFilterLabel label={field.label} />{renderControl(field)}</label>)}
      <div className="xft-filter-bar__actions xft-filter-bar__actions--advanced" aria-label="筛选操作">{controls}</div>
    </div>
  </section>;
}
