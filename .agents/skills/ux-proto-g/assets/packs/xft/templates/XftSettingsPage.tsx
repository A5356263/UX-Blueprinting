import React, { ReactNode, useRef, useState } from "react";
import { Collapse } from "antd";
import type { CollapseProps } from "antd";
import "./XftSettingsPage.css";

export type XftSettingsItem = {
  key: string;
  title?: ReactNode;
  
  description?: ReactNode;
  
  body?: ReactNode;
  
  action?: ReactNode;
  
  
  control?: ReactNode;
  
  
  details?: ReactNode;
  
};

export type XftSettingsGroup = {
  key: string;
  title: ReactNode;
  items: XftSettingsItem[];
};

export type XftSettingsPageProps = {
  groups: XftSettingsGroup[];
  renderAnchor?: (options: { items: { key: string; href: string; title: ReactNode }[]; getContainer: () => HTMLElement | Window; onNavigate: (key: string) => void }) => ReactNode;
};

export function XftSettingsPage({ groups, renderAnchor }: XftSettingsPageProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [activeKeys, setActiveKeys] = useState<string[]>(() => groups.map((group) => group.key));
  const getGroupId = (key: string) => `xft-settings-group-${key}`;
  const getAnchorContainer = () => {
    let parent = rootRef.current?.parentElement;
    while (parent) {
      const overflowY = window.getComputedStyle(parent).overflowY;
      if (overflowY === "auto" || overflowY === "scroll") return parent;
      parent = parent.parentElement;
    }
    return window;
  };
  const getCollapseItems = (group: XftSettingsGroup): CollapseProps["items"] => [{
    key: group.key,
    label: <span id={getGroupId(group.key)}>{group.title}</span>,
    children: <div className="xft-settings-page__items">
      {group.items.map((item) => <div className="xft-settings-page__item" key={item.key}>
        <div className="xft-settings-page__item-main">
          <div className="xft-settings-page__item-content">
            {item.title ? <div className="xft-settings-page__item-title">{item.title}</div> : null}
            {item.body ? <div className="xft-settings-page__item-body">{item.body}</div> : null}
            
            {item.description ? <div className="xft-settings-page__item-description">{item.description}</div> : null}
            
            
            {item.action ? <div className="xft-settings-page__item-action">{item.action}</div> : null}
            
          </div>
          
          {item.control ? <div className="xft-settings-page__item-control">{item.control}</div> : null}
          
        </div>
        
        {item.details ? <div className="xft-settings-page__item-details">{item.details}</div> : null}
        
      </div>)}
    </div>
  }];

  const handleGroupChange = (groupKey: string, keys: string | string[]) => {
    const isOpen = (Array.isArray(keys) ? keys : [keys]).includes(groupKey);
    setActiveKeys((currentKeys) => isOpen
      ? currentKeys.includes(groupKey) ? currentKeys : [...currentKeys, groupKey]
      : currentKeys.filter((key) => key !== groupKey));
  };

  return <main className="xft-settings-page__surface" data-xft-workspace-layout="managed" data-xft-scroll-owner="template"><div className="xft-settings-page" ref={rootRef}>
    <div className={renderAnchor ? "xft-settings-page__centered xft-settings-page__centered--with-anchor" : "xft-settings-page__centered"}>
      {renderAnchor && <aside className="xft-settings-page__anchor" aria-label="设置分区导航">
        {renderAnchor({ items: groups.map((group) => ({ key: group.key, href: `#${getGroupId(group.key)}`, title: group.title })), getContainer: getAnchorContainer, onNavigate: (key) => setActiveKeys((keys) => keys.includes(key) ? keys : [...keys, key]) })}
      </aside>}
      <div className="xft-settings-page__content">
        <div className="xft-settings-page__groups">
          {groups.map((group) => <Collapse
            activeKey={activeKeys.includes(group.key) ? [group.key] : []}
            classNames={{ header: "xft-settings-page__group-header", title: "xft-settings-page__group-title" }}
            expandIconPosition="start"
            items={getCollapseItems(group)}
            key={group.key}
            onChange={(keys) => handleGroupChange(group.key, keys)}
          />)}
        </div>
      </div>
    </div>
  </div></main>;
}
