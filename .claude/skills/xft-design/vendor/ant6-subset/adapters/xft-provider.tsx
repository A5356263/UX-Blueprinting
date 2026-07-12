import type { PropsWithChildren } from "react";
import type { XftThemeConfig } from "../../../design-systems/antd-theme";

type Props = PropsWithChildren<{
  theme?: XftThemeConfig;
}>;

export function XftDesignProvider({ children }: Props) {
  return <>{children}</>;
}
