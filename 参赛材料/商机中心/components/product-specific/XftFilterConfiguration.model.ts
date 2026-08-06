export type XftFilterOperator = "equals" | "contains" | "startsWith";
export type XftFilterField = { key: string; label: string; operators: XftFilterOperator[] };
export type XftFilterSetting = { key: string; enabled: boolean; operator: XftFilterOperator; defaultValue: string };
