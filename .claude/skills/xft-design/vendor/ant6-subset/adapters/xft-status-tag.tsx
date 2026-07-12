import type { PropsWithChildren } from "react";

export type XftStatusTone = "default" | "success" | "warning" | "error" | "info";

export type XftStatusTagProps = PropsWithChildren<{
  tone?: XftStatusTone;
}>;

export function XftStatusTag({
  tone = "default",
  children,
}: XftStatusTagProps) {
  return <span className={`xft-tag xft-tag--${tone}`}>{children}</span>;
}
