// ux-proto-template: template.application-frame 0f5ed833016cd6f8aa27e9547976eb93ad72350e1888c04725da0ed19caed627
import React, { useEffect, useState, type ReactNode } from "react";
import { LeftOutlined } from "@ant-design/icons";
import { Layout, Menu } from "antd";
import { XftTopBar, type XftTopBarProps } from "./application-frame/XftTopBar";
import { XftWorkspaceTabBar, type XftWorkspaceTabBarProps } from "./application-frame/XftWorkspaceTabBar";
import "./XftApplicationFrame.css";

export type XftFrameItem = { key: string; label: string };
type XftWorkspaceSubpage = { title: string; content: ReactNode };
type XftWorkspaceNavigation = {
  openSubpage: (action: { currentTarget: HTMLElement }, content: ReactNode) => void;
};

export type XftApplicationFrameProps = {
  /** Stable module destinations in the workspace, e.g. Module page A / Module page B. Page-local views, modes, filters, and content switching belong in children. This Template does not express product-level primary navigation. */
  sideNavigationItems: XftFrameItem[];
  activeSideNavigationKey?: string;
  onSideNavigationChange?: (key: string) => void;
  globalActions?: ReactNode;
  topBar?: XftTopBarProps;
  workspaceTabBar: XftWorkspaceTabBarProps;
  children: ReactNode | ((navigation: XftWorkspaceNavigation) => ReactNode);
};

export function XftApplicationFrame({ sideNavigationItems, activeSideNavigationKey, onSideNavigationChange, globalActions, topBar, workspaceTabBar, children }: XftApplicationFrameProps) {
  const selectedSideNavigationKey = activeSideNavigationKey || sideNavigationItems[0]?.key || "";
  const { activeKey, tabs } = workspaceTabBar;
  const [subpagesByTab, setSubpagesByTab] = useState(() => new Map<string, XftWorkspaceSubpage[]>());
  const activeDepth = subpagesByTab.get(activeKey)?.length ?? 0;

  useEffect(() => {
    const openTabKeys = new Set(tabs.map((tab) => tab.key));
    setSubpagesByTab((current) => {
      const remaining = new Map([...current].filter(([key]) => openTabKeys.has(key)));
      return remaining.size === current.size ? current : remaining;
    });
  }, [tabs]);

  const openSubpage: XftWorkspaceNavigation["openSubpage"] = ({ currentTarget }, content) => {
    const title = currentTarget.innerText.trim().replace(/\s+/g, " ") || currentTarget.getAttribute("aria-label")?.trim();
    if (!title) throw new Error("An action that opens a subpage must have a visible label or an aria-label.");
    setSubpagesByTab((current) => {
      const next = new Map(current);
      next.set(activeKey, [...(current.get(activeKey) ?? []), { title, content }]);
      return next;
    });
  };

  const goBack = () => {
    setSubpagesByTab((current) => {
      const stack = current.get(activeKey);
      if (!stack?.length) return current;
      const next = new Map(current);
      if (stack.length === 1) next.delete(activeKey);
      else next.set(activeKey, stack.slice(0, -1));
      return next;
    });
  };

  const renderViewport = (content: ReactNode, hidden: boolean, title?: string, key?: string) => (
    <div key={key} className="xft-frame__content-viewport" hidden={hidden}>
      {title && <div className="xft-frame__subpage-header">
        <button className="xft-frame__subpage-back" type="button" onClick={goBack}>
          <LeftOutlined aria-hidden="true" />
          <span>返回</span>
        </button>
        <span className="xft-frame__subpage-divider" aria-hidden="true" />
        <span className="xft-frame__subpage-title" title={title}>{title}</span>
      </div>}
      <div className="xft-frame__canvas">
        <div className="xft-frame__work-surface">
          <div className="xft-frame__content">{content}</div>
        </div>
      </div>
    </div>
  );

  const rootContent = typeof children === "function" ? children({ openSubpage }) : children;
  return <Layout className="xft-frame">
    <XftTopBar {...(topBar ?? {})} globalActions={globalActions ?? topBar?.globalActions} />
    <Layout className="xft-frame__body">
      <Layout.Sider className="xft-frame__sider" width={188}>
        <Menu mode="inline" selectedKeys={selectedSideNavigationKey ? [selectedSideNavigationKey] : []} items={sideNavigationItems} onClick={({ key }) => onSideNavigationChange?.(String(key))} />
      </Layout.Sider>
      <Layout.Content className="xft-frame__workspace">
        <div className="xft-frame__workspace-top"><XftWorkspaceTabBar {...workspaceTabBar} /></div>
        {renderViewport(rootContent, activeDepth > 0)}
        {[...subpagesByTab].flatMap(([tabKey, stack]) => stack.map((page, index) => renderViewport(
          page.content,
          tabKey !== activeKey || index !== stack.length - 1,
          page.title,
          JSON.stringify([tabKey, index]),
        )))}
      </Layout.Content>
    </Layout>
  </Layout>;
}
