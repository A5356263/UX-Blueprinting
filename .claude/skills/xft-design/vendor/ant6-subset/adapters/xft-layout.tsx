import type { PropsWithChildren, ReactNode } from "react";

export type XftMenuItem = {
  key: string;
  label: string;
};

export type XftAdminSideShellProps = PropsWithChildren<{
  title: string;
  menuItems: XftMenuItem[];
  selectedKey: string;
  topExtra?: ReactNode;
}>;

export function XftAdminSideShell({
  title,
  menuItems,
  selectedKey,
  topExtra,
  children,
}: XftAdminSideShellProps) {
  return (
    <div className="xft-shell">
      <aside className="xft-shell__sider">
        <div className="xft-shell__brand">{title}</div>
        <nav className="xft-shell__menu" aria-label="主导航">
          {menuItems.map((item) => (
            <button
              key={item.key}
              type="button"
              className={
                item.key === selectedKey
                  ? "xft-shell__menu-item xft-shell__menu-item--active"
                  : "xft-shell__menu-item"
              }
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="xft-shell__main">
        <header className="xft-shell__header">
          <span className="xft-shell__header-title">XFT React Prototype</span>
          {topExtra}
        </header>
        <div className="xft-shell__content">{children}</div>
      </main>
    </div>
  );
}
