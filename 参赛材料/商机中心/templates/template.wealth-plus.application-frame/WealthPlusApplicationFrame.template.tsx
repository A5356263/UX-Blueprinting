import React, { ReactNode } from "react";
import { Button, Typography } from "antd";
import "./WealthPlusApplicationFrame.css";

export type WealthPlusPrimaryNavigationItem = {
  key: string;
  label: string;
  onClick?: () => void;
};

export type WealthPlusApplicationFrameProps = {
  brand?: ReactNode;
  primaryNavigationItems: WealthPlusPrimaryNavigationItem[];
  activePrimaryNavigationKey: string;
  globalActions?: ReactNode;
  pageTitle?: string;
  children: ReactNode;
};

/**
 * 企业财富+桌面页面框架。
 *
 * 页面查询筛选项由 children 提供。筛选控件不得显示前置字段名；应通过
 * Input placeholder 或 Select placeholder 在控件内部表达条件，例如“管理机构”。
 */
export function WealthPlusApplicationFrame({
  brand = "企业财富+",
  primaryNavigationItems,
  activePrimaryNavigationKey,
  globalActions,
  pageTitle,
  children,
}: WealthPlusApplicationFrameProps) {
  return <div className="wealth-plus-frame">
    <header className="wealth-plus-frame__top-navigation">
      <div className="wealth-plus-frame__brand">{brand}</div>
      <nav className="wealth-plus-frame__primary-navigation" aria-label="一级菜单">
        {primaryNavigationItems.map((item) => <Button
          className="wealth-plus-frame__primary-navigation-item"
          data-active={item.key === activePrimaryNavigationKey ? "true" : "false"}
          key={item.key}
          type="text"
          onClick={item.onClick}
        >{item.label}</Button>)}
      </nav>
      {globalActions ? <div className="wealth-plus-frame__global-actions">{globalActions}</div> : null}
    </header>
    <main className="wealth-plus-frame__workspace">
      <section className="wealth-plus-frame__primary-panel">
        {pageTitle ? <Typography.Title className="wealth-plus-frame__page-title" level={4}>{pageTitle}</Typography.Title> : null}
        {children}
      </section>
    </main>
  </div>;
}
