import type { ReactNode } from "react";

export type XftFilterMode = "header" | "realtime-scheme" | "precondition" | "group-finance" | "quick";
export type XftAuxiliaryRow = { type: string; accounts: string[]; field: string; operator: string; values: string[] };
export type XftFilterValue = string | string[] | boolean | [string, string] | XftAuxiliaryRow[] | Record<string, unknown> | null | undefined;
export type XftFilterValues = Record<string, XftFilterValue>;
export type XftFilterField = {
  key: string;
  label: string;
  type?: "text" | "search" | "select" | "multi-select" | "month-range" | "date-range" | "number-range" | "checkbox";
  options?: { label: string; value: string }[];
  placeholder?: string;
  required?: boolean;
  showInPanel?: boolean;
  showInManager?: boolean;
  /** Keep the opposite month in sync when the user reverses the range. */
  autoAdjustRange?: boolean;
  /** Business-specific fields, such as auxiliary accounting rows, can supply their own control. */
  render?: (value: XftFilterValue, change: (value: XftFilterValue) => void) => ReactNode;
  summarize?: (value: XftFilterValue) => string;
  summaryItems?: (value: XftFilterValue) => { id: string; text: string; title?: string; nextValue: XftFilterValue }[];
};
export type XftFilterScheme = { id: string; name: string; values: XftFilterValues; isDefault?: boolean };
export type XftSchemeManagerTableBinding = {
  schemes: XftFilterScheme[];
  onRename: (id: string, name: string) => void;
  onDefault: (id: string) => void;
  onDelete: (id: string) => void;
};
export type XftFilterTableBinding = {
  filterValues: XftFilterValues;
  busy: boolean;
  renderColumnFilter: (key: string, close: () => void) => ReactNode;
};
