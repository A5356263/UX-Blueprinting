export type XftThemeConfig = {
  token: Record<string, string | number>;
  components: Record<string, Record<string, string | number>>;
};

// 第一阶段先保留“Ant 风格主题桥接”的命名，承接旧认知，
// 但正式类型契约已切换为本地 vendor 可消费的主题对象。
export const xftAntdTheme: XftThemeConfig = {
  token: {
    colorPrimary: "#1966ff",
    colorSuccess: "#0ac767",
    colorWarning: "#ff9326",
    colorError: "#fa4332",
    colorInfo: "#1966ff",
    colorBgBase: "#ffffff",
    colorBgLayout: "#f3f4f6",
    colorText: "rgba(19, 34, 64, 0.95)",
    colorTextSecondary: "rgba(19, 34, 64, 0.65)",
    colorBorder: "rgba(19, 34, 64, 0.15)",
    colorSplit: "rgba(19, 34, 64, 0.1)",
    borderRadius: 6,
    fontSize: 14,
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", Arial, sans-serif',
    controlHeight: 32,
  },
  components: {
    Layout: {
      bodyBg: "#f3f4f6",
      headerBg: "#ffffff",
      siderBg: "#132240",
      triggerBg: "#132240",
    },
    Card: {
      borderRadiusLG: 12,
      paddingLG: 24,
    },
    Table: {
      headerBg: "#ffffff",
      rowHoverBg: "rgba(19, 34, 64, 0.02)",
      borderColor: "rgba(19, 34, 64, 0.1)",
      cellPaddingBlock: 12,
    },
    Button: {
      borderRadius: 6,
      controlHeight: 32,
      primaryShadow: "none",
    },
    Input: {
      activeBorderColor: "#1966ff",
      hoverBorderColor: "#4086ff",
    },
    Select: {
      optionSelectedBg: "#ebf3ff",
      activeBorderColor: "#1966ff",
      hoverBorderColor: "#4086ff",
    },
    Tag: {
      defaultBg: "rgba(19, 34, 64, 0.05)",
      defaultColor: "rgba(19, 34, 64, 0.85)",
    },
  },
};
