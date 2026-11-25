import React, { CSSProperties, ReactNode, useCallback, useEffect, useRef, useState } from "react";

import { Input } from "antd";

import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";

import { SearchOutlined } from "@ant-design/icons";

import "./XftContextSelectorPanel.css";

export type XftContextSelectorPanelProps = {
  directoryContent: ReactNode;
  directoryWidth?: number;
  onDirectoryWidthChange?: (width: number) => void;

  directoryHeader?: ReactNode;

  directorySearchValue?: string;
  onDirectorySearchChange?: (value: string) => void;
  directorySearchPlaceholder?: string;

  directoryActions?: ReactNode;

  directoryFooter?: ReactNode;

  directoryCollapsible?: boolean;
  directoryCollapsed?: boolean;
  onDirectoryCollapsedChange?: (collapsed: boolean) => void;

};

export function XftContextSelectorPanel({
  directoryContent, directoryWidth = 200, onDirectoryWidthChange,
  
  directoryHeader,

  directorySearchValue, onDirectorySearchChange, directorySearchPlaceholder = "搜索",

  directoryActions,

  directoryFooter,
  
  directoryCollapsible = false, directoryCollapsed, onDirectoryCollapsedChange
}: XftContextSelectorPanelProps) {
  const frameRef = useRef<HTMLElement>(null);
  const [innerDirectoryCollapsed, setInnerDirectoryCollapsed] = useState(false);

  const [innerDirectorySearchValue, setInnerDirectorySearchValue] = useState("");

  const [directoryWidthState, setDirectoryWidthState] = useState(directoryWidth);
  const [resizingDirectory, setResizingDirectory] = useState(false);
  const isDirectoryCollapsed = directoryCollapsed ?? innerDirectoryCollapsed;
  const clampDirectoryWidth = useCallback((nextWidth: number) => {
    const frameWidth = frameRef.current?.parentElement?.clientWidth ?? 768;
    return Math.max(48, Math.min(384, Math.floor(frameWidth / 2), Math.max(200, nextWidth)));
  }, []);
  const updateDirectoryWidth = useCallback((nextWidth: number) => {
    const clampedWidth = clampDirectoryWidth(nextWidth);
    setDirectoryWidthState(clampedWidth);
    onDirectoryWidthChange?.(clampedWidth);
  }, [clampDirectoryWidth, onDirectoryWidthChange]);
  useEffect(() => {
    setDirectoryWidthState(isDirectoryCollapsed ? 48 : clampDirectoryWidth(directoryWidth));
  }, [clampDirectoryWidth, directoryWidth, isDirectoryCollapsed]);
  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;
    const observer = new ResizeObserver(() => setDirectoryWidthState((currentWidth) => isDirectoryCollapsed ? 48 : clampDirectoryWidth(currentWidth)));
    observer.observe(frame.parentElement ?? frame);
    return () => observer.disconnect();
  }, [clampDirectoryWidth, isDirectoryCollapsed]);
  useEffect(() => {
    if (!resizingDirectory || isDirectoryCollapsed) return;
    const handlePointerMove = (event: PointerEvent) => {
      const frame = frameRef.current;
      if (frame) updateDirectoryWidth(event.clientX - frame.getBoundingClientRect().left);
    };
    const stopResizing = () => setResizingDirectory(false);
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", stopResizing);
    window.addEventListener("pointercancel", stopResizing);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", stopResizing);
      window.removeEventListener("pointercancel", stopResizing);
    };
  }, [isDirectoryCollapsed, resizingDirectory, updateDirectoryWidth]);

  const currentDirectorySearchValue = directorySearchValue ?? innerDirectorySearchValue;

  const toggleDirectoryCollapsed = () => {
    const next = !isDirectoryCollapsed;
    if (directoryCollapsed === undefined) setInnerDirectoryCollapsed(next);
    onDirectoryCollapsedChange?.(next);
  };

  const changeDirectorySearch = (value: string) => {
    if (directorySearchValue === undefined) setInnerDirectorySearchValue(value);
    onDirectorySearchChange?.(value);
  };
  const hasDirectorySearch = Boolean(onDirectorySearchChange);

  const directoryToggle = directoryCollapsible ? <button type="button" className="xft-context-selector-panel__directory-toggle" aria-label={isDirectoryCollapsed ? "展开左侧选择区" : "折叠左侧选择区"} onClick={toggleDirectoryCollapsed}>{isDirectoryCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}</button> : null;
  const leftContent = isDirectoryCollapsed ? <div className="xft-context-selector-panel__directory xft-context-selector-panel__directory--collapsed">{directoryToggle}</div> : <div className="xft-context-selector-panel__directory">
    {(directoryHeader ||  directoryToggle) ? <div className="xft-context-selector-panel__directory-header">
      {directoryHeader ? <div className="xft-context-selector-panel__directory-title">{directoryHeader}</div> : <span />}
      {directoryToggle}
    </div> : null}
    {hasDirectorySearch ? <div className="xft-context-selector-panel__directory-search"><Input value={currentDirectorySearchValue} allowClear placeholder={directorySearchPlaceholder} prefix={<SearchOutlined />} onChange={(event) => changeDirectorySearch(event.target.value)} /></div> : null}
    {directoryActions ? <div className="xft-context-selector-panel__directory-actions">{directoryActions}</div> : null}
    <div className="xft-context-selector-panel__directory-content">{directoryContent}</div>
    {directoryFooter ? <div className="xft-context-selector-panel__directory-footer">{directoryFooter}</div> : null}
  </div>;
  return <aside ref={frameRef} className="xft-context-selector-panel" style={{ width: directoryWidthState }}>
    {leftContent}
    {!isDirectoryCollapsed ? <div className="xft-context-selector-panel__resize-handle" role="separator" aria-label="调整范围面板宽度" aria-orientation="vertical" onPointerDown={(event) => { event.preventDefault(); setResizingDirectory(true); }} /> : null}
  </aside>;
}


