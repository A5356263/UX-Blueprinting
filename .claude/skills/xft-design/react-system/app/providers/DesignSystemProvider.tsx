import type { PropsWithChildren } from "react";
import { xftAntdTheme } from "../../../design-systems/antd-theme";
import { XftDesignProvider } from "../../../vendor/ant6-subset/adapters/xft-provider";

export function DesignSystemProvider({ children }: PropsWithChildren) {
  return <XftDesignProvider theme={xftAntdTheme}>{children}</XftDesignProvider>;
}
