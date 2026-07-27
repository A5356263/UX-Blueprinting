import React, { ReactNode } from "react";
import "./XftContentActionBar.css";

export type XftContentActionBarProps = {
  children: ReactNode;
  ariaLabel: string;
};

export function XftContentActionBar({ children, ariaLabel }: XftContentActionBarProps) {
  return <div className="xft-content-action-bar" role="toolbar" aria-label={ariaLabel}>{children}</div>;
}
