import React, { ReactNode } from "react";
import "./XftPrimaryWorkSurface.css";

export type XftPrimaryWorkSurfaceProps = {
  children: ReactNode;
};

export function XftPrimaryWorkSurface({ children }: XftPrimaryWorkSurfaceProps) {
  return <main className="xft-primary-work-surface">{children}</main>;
}
