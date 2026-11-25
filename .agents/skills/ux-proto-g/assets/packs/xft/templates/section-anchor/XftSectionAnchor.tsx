import React, { ReactNode, useEffect, useState } from "react";
import "./XftSectionAnchor.css";

export type XftSectionAnchorItem = {
  key: string;
  href: string;
  title: ReactNode;
};

export type XftSectionAnchorProps = {
  items: XftSectionAnchorItem[];
  getContainer?: () => HTMLElement | Window;
  onNavigate?: (key: string) => void;
  ariaLabel?: string;
};

export function XftSectionAnchor({ items, getContainer, onNavigate, ariaLabel = "分区导航" }: XftSectionAnchorProps) {
  const [activeKey, setActiveKey] = useState(items[0]?.key ?? "");
  const getTarget = (href: string) => href.startsWith("#") ? document.getElementById(href.slice(1)) : null;

  useEffect(() => {
    const container = getContainer?.() ?? window;
    const updateActiveItem = () => {
      const isAtBottom = container instanceof Window
        ? window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 1
        : container.scrollTop + container.clientHeight >= container.scrollHeight - 1;
      if (isAtBottom) {
        setActiveKey(items.at(-1)?.key ?? "");
        return;
      }
      const containerTop = container instanceof Window ? 0 : container.getBoundingClientRect().top;
      const visibleItems = items.filter((item) => {
        const target = getTarget(item.href);
        return target && target.getBoundingClientRect().top <= containerTop + 8;
      });
      setActiveKey((visibleItems.at(-1) ?? items[0])?.key ?? "");
    };

    updateActiveItem();
    container.addEventListener("scroll", updateActiveItem, { passive: true });
    return () => container.removeEventListener("scroll", updateActiveItem);
  }, [getContainer, items]);

  const handleNavigate = (event: React.MouseEvent<HTMLAnchorElement>, item: XftSectionAnchorItem) => {
    event.preventDefault();
    onNavigate?.(item.key);
    const target = getTarget(item.href);
    if (!target) return;

    setActiveKey(item.key);
    const container = getContainer?.() ?? window;
    if (container instanceof Window) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    container.scrollTo({
      top: container.scrollTop + target.getBoundingClientRect().top - container.getBoundingClientRect().top,
      behavior: "smooth"
    });
  };

  return <nav className="xft-section-anchor" aria-label={ariaLabel}>
    <ul className="xft-section-anchor__list">
      {items.map((item) => <li className="xft-section-anchor__item" key={item.key} data-active={item.key === activeKey ? "true" : "false"}>
        <a className="xft-section-anchor__link" href={item.href} aria-current={item.key === activeKey ? "location" : undefined} onClick={(event) => handleNavigate(event, item)}>{item.title}</a>
      </li>)}
    </ul>
  </nav>;
}
