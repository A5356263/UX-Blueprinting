import React from "react";
import { Button, Card, Checkbox, Input, Select, Space, Tag, Typography } from "antd";
import { XftFilterField, XftFilterSetting } from "./XftFilterConfiguration.model";
import "./XftFilterConfiguration.css";

export type XftFilterConfigurationProps = { fields: XftFilterField[]; value: XftFilterSetting[]; defaults: XftFilterSetting[]; onChange: (next: XftFilterSetting[]) => void };

export function XftFilterConfiguration({ fields, value, defaults, onChange }: XftFilterConfigurationProps) {
  const byKey = new Map(value.map((setting) => [setting.key, setting]));
  const settingFor = (field: XftFilterField): XftFilterSetting => byKey.get(field.key) ?? { key: field.key, enabled: false, operator: field.operators[0], defaultValue: "" };
  const update = (field: XftFilterField, patch: Partial<XftFilterSetting>) => {
    const current = byKey.get(field.key);
    onChange(current ? value.map((setting) => setting.key === field.key ? { ...setting, ...patch } : setting) : [...value, { ...settingFor(field), ...patch }]);
  };
  const changed = JSON.stringify(value) !== JSON.stringify(defaults);
  return <Card className="xft-filter-config" data-od-id="xft-filter-configuration"><div className="xft-filter-config__body">
    <Space className="xft-filter-config__heading" align="center"><Typography.Title className="xft-filter-config__title" level={4}>Filter configuration</Typography.Title>{changed ? <Tag color="blue">Edited</Tag> : <Tag>Default</Tag>}</Space>
    {fields.length === 0 ? <Typography.Text type="secondary">No configurable fields</Typography.Text> : <div className="xft-filter-config__layout">
      <section className="xft-filter-config__catalog" aria-label="Available filter fields">
        <Typography.Text strong>Available fields</Typography.Text>
        <div className="xft-filter-config__field-list">{fields.map((field) => {
          const setting = settingFor(field);
          return <Checkbox key={field.key} checked={setting.enabled} onChange={(event) => update(field, { enabled: event.target.checked })}>{field.label}</Checkbox>;
        })}</div>
      </section>
      <section className="xft-filter-config__selected" aria-label="Enabled filter fields">
        <Typography.Text strong>Enabled fields</Typography.Text>
        {fields.filter((field) => settingFor(field).enabled).length === 0 ? <Typography.Text type="secondary">Select fields to configure</Typography.Text> : fields.filter((field) => settingFor(field).enabled).map((field) => {
          const setting = settingFor(field);
          return <div className="xft-filter-config__row" key={field.key}>
            <Typography.Text>{field.label}</Typography.Text>
            <Select value={setting.operator} options={field.operators.map((operator) => ({ value: operator, label: operator }))} onChange={(operator) => update(field, { operator })} />
            <Input value={setting.defaultValue} placeholder="Default value" onChange={(event) => update(field, { defaultValue: event.target.value })} />
          </div>;
        })}
      </section>
    </div>}
    <div className="xft-filter-config__footer"><Button disabled={!changed} onClick={() => onChange(defaults)}>Reset defaults</Button></div>
  </div></Card>;
}
