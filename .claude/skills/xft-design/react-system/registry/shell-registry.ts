export const shellRegistry = [
  {
    id: "admin-side-shell",
    layer: "shell",
    pageTypes: ["list", "form", "detail"],
    summary: "企业后台默认侧边导航型页面壳。",
    allows: ["title", "menuItems", "selectedKey", "topExtra", "children"],
  },
  {
    id: "admin-top-shell",
    layer: "shell",
    pageTypes: ["message", "light-task"],
    summary: "无持续侧边导航时的顶部导航壳。",
    allows: ["title", "menuItems", "selectedKey", "topExtra", "children"],
  },
] as const;
