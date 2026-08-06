import React, { ReactNode } from "react";
import { Layout, Menu, Typography } from "antd";
import "./XftApplicationFrame.css";

export type XftFrameItem = { key: string; label: string };
export type XftApplicationFrameProps = {
  /** Stable module destinations in the workspace, e.g. Module page A / Module page B. Page-local views, modes, filters, and content switching belong in children. This Template does not express product-level primary navigation. */
  sideNavigationItems: XftFrameItem[];
  activeSideNavigationKey: string;
  globalActions?: ReactNode;
  workspaceTop?: ReactNode;
  workspaceBottomDock?: ReactNode;
  children: ReactNode;
};

export function XftApplicationFrame({ sideNavigationItems, activeSideNavigationKey, globalActions, workspaceTop, workspaceBottomDock, children }: XftApplicationFrameProps) {
  return <Layout className="xft-frame">
    <header className="xft-frame__header">
      <Typography.Title className="xft-frame__brand" level={4}>XFT</Typography.Title>
      {globalActions ? <div className="xft-frame__global-actions">{globalActions}</div> : null}
    </header>
    <Layout className="xft-frame__body">
      <Layout.Sider className="xft-frame__sider" width={188}>
        <Menu mode="inline" selectedKeys={[activeSideNavigationKey]} items={sideNavigationItems} />
      </Layout.Sider>
      <Layout.Content className="xft-frame__workspace">
        {workspaceTop ? <div className="xft-frame__workspace-top">{workspaceTop}</div> : null}
        <div className="xft-frame__content-viewport">
          <div className="xft-frame__canvas">{children}</div>
          {workspaceBottomDock ? <div className="xft-frame__workspace-bottom-dock">{workspaceBottomDock}</div> : null}
        </div>
      </Layout.Content>
    </Layout>
  </Layout>;
}
