import React, { useLayoutEffect, useRef, useState } from "react";
import {
  CloseOutlined,
  LeftOutlined,
  MoreOutlined,
  RightOutlined,
} from "@ant-design/icons";
import { Dropdown } from "antd";
import "./XftWorkspaceTabBar.css";

export type XftWorkspaceTab = {
  key: string;
  label: string;
  closable?: boolean;
};

export type XftWorkspaceTabBarProps = {
  tabs: XftWorkspaceTab[];
  activeKey: string;
  onActivate: (key: string) => void;
  onClose: (key: string) => void;
  onNavigate: (direction: -1 | 1) => void;
  onCloseAll: () => void;
};

export function XftWorkspaceTabBar({ tabs, activeKey, onActivate, onClose, onNavigate, onCloseAll }: XftWorkspaceTabBarProps) {
  const tabSliderRef = useRef<HTMLDivElement>(null);
  const tabContentRef = useRef<HTMLDivElement>(null);
  const [hasOverflow, setHasOverflow] = useState(false);
  const activeIndex = tabs.findIndex((tab) => tab.key === activeKey);
  const canNavigatePrevious = activeIndex > 0;
  const canNavigateNext = activeIndex >= 0 && activeIndex < tabs.length - 1;
  const canCloseTabs = tabs.length > 1;

  useLayoutEffect(() => {
    const slider = tabSliderRef.current;
    const content = tabContentRef.current;
    if (!slider || !content) return;

    const measureOverflow = () => {
      setHasOverflow(content.scrollWidth > slider.clientWidth);
    };

    measureOverflow();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measureOverflow);
    observer?.observe(slider);
    observer?.observe(content);
    window.addEventListener("resize", measureOverflow);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measureOverflow);
    };
  }, [tabs]);

  const overflowMenu = <div className="xft-workspace-tab-bar__overflow-menu" role="menu">
    <div className="xft-workspace-tab-bar__overflow-list">
      {tabs.map((tab) => <div
        className={`xft-workspace-tab-bar__overflow-item${tab.key === activeKey ? " xft-workspace-tab-bar__overflow-item--active" : ""}`}
        key={tab.key}
        role="menuitem"
        tabIndex={0}
        onClick={() => onActivate(tab.key)}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") onActivate(tab.key);
        }}
      >
        <span className="xft-workspace-tab-bar__overflow-name">{tab.label}</span>
        {tab.closable !== false && canCloseTabs ? <button
          className="xft-workspace-tab-bar__overflow-close"
          type="button"
          aria-label={`关闭 ${tab.label}`}
          onClick={(event) => {
            event.stopPropagation();
            onClose(tab.key);
          }}
        >
          <CloseOutlined aria-hidden="true" />
        </button> : null}
      </div>)}
    </div>
    <div className="xft-workspace-tab-bar__overflow-divider" />
    <button className="xft-workspace-tab-bar__close-all" type="button" onClick={onCloseAll} disabled={!canCloseTabs}>关闭全部</button>
  </div>;

  return <div className="xft-workspace-tab-bar">
    <div className="xft-workspace-tab-bar__tab-slider" ref={tabSliderRef}>
      <div className="xft-workspace-tab-bar__tab-slide-content" ref={tabContentRef} role="tablist" aria-label="工作区标签">
        {tabs.map((tab) => <div
          className={`xft-workspace-tab-bar__tab-item${tab.key === activeKey ? " xft-workspace-tab-bar__tab-item--active" : ""}`}
          key={tab.key}
          role="tab"
          aria-selected={tab.key === activeKey}
          tabIndex={tab.key === activeKey ? 0 : -1}
          onClick={() => onActivate(tab.key)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") onActivate(tab.key);
          }}
        >
          <span className="xft-workspace-tab-bar__tab-name">{tab.label}</span>
          {tab.closable !== false && canCloseTabs ? <button
            className="xft-workspace-tab-bar__tab-close"
            type="button"
            aria-label={`关闭 ${tab.label}`}
            onClick={(event) => {
              event.stopPropagation();
              onClose(tab.key);
            }}
          >
            <CloseOutlined aria-hidden="true" />
          </button> : null}
          <span className="xft-workspace-tab-bar__left-corner" aria-hidden="true" />
          <span className="xft-workspace-tab-bar__right-corner" aria-hidden="true" />
        </div>)}
      </div>
    </div>

    {hasOverflow ? <div className="xft-workspace-tab-bar__right-opr-area">
      <button
        className="xft-workspace-tab-bar__control xft-workspace-tab-bar__prev-page"
        type="button"
        aria-label="上一个工作区标签"
        disabled={!canNavigatePrevious}
        onClick={() => onNavigate(-1)}
      >
        <LeftOutlined aria-hidden="true" />
      </button>
      <button
        className="xft-workspace-tab-bar__control xft-workspace-tab-bar__next-page"
        type="button"
        aria-label="下一个工作区标签"
        disabled={!canNavigateNext}
        onClick={() => onNavigate(1)}
      >
        <RightOutlined aria-hidden="true" />
      </button>
      <Dropdown dropdownRender={() => overflowMenu} trigger={["click"]} placement="bottomRight">
        <button className="xft-workspace-tab-bar__control xft-workspace-tab-bar__more" type="button" aria-label="更多工作区标签">
          <MoreOutlined aria-hidden="true" />
        </button>
      </Dropdown>
    </div> : null}
  </div>;
}
