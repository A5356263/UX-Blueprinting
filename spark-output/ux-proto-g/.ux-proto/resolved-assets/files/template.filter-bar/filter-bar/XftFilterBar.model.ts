import type { Dayjs } from "dayjs";

export type XftFilterBarControlType = "input" | "select" | "date" | "range";
export type XftFilterBarOption = { label: string; value: string };
export type XftFilterBarValue = string | Dayjs | null | [Dayjs | null, Dayjs | null] | undefined;
export type XftFilterBarValues = Record<string, XftFilterBarValue>;

export type XftFilterBarField = {
  key: string;
  label: string;
  type?: XftFilterBarControlType;
  placeholder?: string;
  options?: XftFilterBarOption[];
  /** 兼容历史调用；不再控制更多筛选展示规则。 */
  collapsed?: boolean;
  /** 兼容历史调用；不再控制更多筛选展示规则。 */
  advanced?: boolean;
  disabled?: boolean;
};
