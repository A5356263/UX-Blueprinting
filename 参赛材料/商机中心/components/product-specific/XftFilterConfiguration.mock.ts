import { XftFilterField, XftFilterSetting } from "./XftFilterConfiguration.model";

export const mockXftFilterFields: XftFilterField[] = [
  { key: "documentNo", label: "Document number", operators: ["equals", "contains", "startsWith"] },
  { key: "supplier", label: "Supplier", operators: ["equals", "contains"] },
  { key: "status", label: "Status", operators: ["equals"] }
];

export const mockXftFilterSettings: XftFilterSetting[] = [
  { key: "documentNo", enabled: true, operator: "contains", defaultValue: "" },
  { key: "supplier", enabled: true, operator: "equals", defaultValue: "" },
  { key: "status", enabled: false, operator: "equals", defaultValue: "Pending" }
];
