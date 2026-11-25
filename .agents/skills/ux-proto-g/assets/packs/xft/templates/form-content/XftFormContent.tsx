import React, { CSSProperties, ReactNode, useEffect, useRef, useState } from "react";
import { Form, Tooltip } from "antd";
import type { FormInstance, FormItemProps } from "antd";

import "./XftFormContent.css";

const columnGap = 24;
const labelGap = 8;
const horizontalSingleWidth = 400;
const horizontalMultiWidth = 320;
const verticalControlWidth = 200;

export type XftFormField = {
  key: string;
  name: string;
  label: ReactNode;
  control: ReactNode;
  rules?: FormItemProps["rules"];
  extra?: FormItemProps["extra"];
  tooltip?: FormItemProps["tooltip"];
  controlWidth?: 80 | 120;
  span?: 1 | 2 | 3 | 4 | "full";
  hidden?: boolean;
};

export type XftFormSection = {
  key: string;
  heading?: ReactNode;
  fields: XftFormField[];
};

export type XftFormContentProps = {
  form?: FormInstance<Record<string, unknown>>;
  sections: XftFormSection[];
  columns?: 1 | 2 | 3 | 4;
  labelLayout?: "horizontal" | "vertical";
  labelWidth?: number;
  initialValues?: Record<string, unknown>;
  loading?: boolean;
  onFinish?: (values: Record<string, unknown>) => void | Promise<void>;
};

type FieldLabelProps = { children: ReactNode };

function FieldLabel({ children }: FieldLabelProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const [overflow, setOverflow] = useState(false);
  const [wrapped, setWrapped] = useState(false);

  useEffect(() => {
    const label = ref.current;
    if (!label) return;

    const measure = () => {
      setOverflow(label.scrollWidth > label.clientWidth || label.scrollHeight > label.clientHeight);
      setWrapped(label.clientHeight > Number.parseFloat(getComputedStyle(label).lineHeight));
    };
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(label);
    return () => observer?.disconnect();
  }, [children]);

  return (
    <Tooltip title={overflow ? children : null} trigger={["hover", "focus"]}>
      <span className="xft-form-content__label" ref={ref} data-wrapped={wrapped || undefined} tabIndex={overflow ? 0 : undefined}>
        {children}
      </span>
    </Tooltip>
  );
}

export function XftFormContent({
  form,
  sections,
  columns = 2,
  labelLayout = "horizontal",
  labelWidth,
  initialValues,
  loading = false,
  onFinish,
}: XftFormContentProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [layout, setLayout] = useState({ columns, labelWidth: labelWidth ?? 72 });
  const horizontal = labelLayout === "horizontal";

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const measure = () => {
      const availableWidth = root.clientWidth;
      if (!availableWidth) return;

      let measuredLabelWidth = 0;
      if (horizontal) {
        const labels = Array.from(root.querySelectorAll<HTMLLabelElement>(
          ".xft-form-content__field > .ant-form-item-row > .ant-form-item-label > label",
        )).filter(label => label.getClientRects().length > 0);
        root.dataset.measuringLabels = "true";
        measuredLabelWidth = Math.ceil(Math.max(0, ...labels.map(label => label.getBoundingClientRect().width)));
        delete root.dataset.measuringLabels;

        const insideWindow = root.closest(".ant-modal, .ant-drawer");
        const defaultWidth = insideWindow ? Math.min(measuredLabelWidth, 128) : measuredLabelWidth;
        measuredLabelWidth = Math.min(labelWidth ?? defaultWidth, Math.floor(availableWidth / 2));
      }

      const columnWidth = horizontal ? measuredLabelWidth + labelGap + horizontalMultiWidth : verticalControlWidth;
      const fittedColumns = Math.floor((availableWidth + columnGap) / (columnWidth + columnGap));
      const visibleColumns = Math.max(1, Math.min(columns, fittedColumns));
      setLayout(previous => previous.columns === visibleColumns && previous.labelWidth === measuredLabelWidth
        ? previous
        : { columns: visibleColumns, labelWidth: measuredLabelWidth });
    };

    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(root);
    window.addEventListener("resize", measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [columns, horizontal, labelWidth, sections]);

  if (!sections?.length) throw new Error("XftFormContent requires sections.");

  const controlWidth = horizontal
    ? layout.columns === 1 ? horizontalSingleWidth : horizontalMultiWidth
    : verticalControlWidth;
  const columnWidth = horizontal ? layout.labelWidth + labelGap + controlWidth : controlWidth;
  const formStyle = {
    "--xft-form-columns": layout.columns,
    "--xft-form-column-width": columnWidth + "px",
    "--xft-form-column-gap": columnGap + "px",
    "--xft-form-label-gap": labelGap + "px",
    "--xft-form-label-width": layout.labelWidth + "px",
    "--xft-form-control-width": controlWidth + "px",
  } as CSSProperties;

  return (
    <div className="xft-form-content" ref={rootRef} data-label-layout={labelLayout} style={formStyle}>
      <Form form={form} layout={labelLayout} colon={false} initialValues={initialValues} disabled={loading} onFinish={onFinish}>
        <div className="xft-form-content__sections">
          {sections.map(section => (
            <section className="xft-form-content__section" id={"xft-form-section-" + section.key} key={section.key}>
              {section.heading != null && <div className="xft-form-content__heading">{section.heading}</div>}
              <div className="xft-form-content__fields">
                {section.fields.map(field => (
                  <Form.Item
                    className="xft-form-content__field"
                    data-span={field.span ?? 1}
                    key={field.key}
                    label={field.label == null ? field.label : <FieldLabel>{field.label}</FieldLabel>}
                    name={field.name}
                    rules={field.rules}
                    hidden={field.hidden}
                    extra={field.extra}
                    tooltip={field.tooltip}
                    style={{
                      gridColumn: field.span === "full" ? "1 / -1" : field.span ? "span " + Math.min(field.span, layout.columns) : undefined,
                      "--xft-form-field-width": field.controlWidth ? field.controlWidth + "px" : undefined,
                    } as CSSProperties}
                  >
                    {field.control}
                  </Form.Item>
                ))}
              </div>
            </section>
          ))}
        </div>
      </Form>
    </div>
  );
}
