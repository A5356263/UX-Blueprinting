import type { PropsWithChildren, ReactNode } from "react";
import { XftAdminSideShell } from "../../../vendor/ant6-subset/adapters/xft-layout";

type Props = PropsWithChildren<{
  title: string;
  menuItems: { key: string; label: string }[];
  selectedKey: string;
  topExtra?: ReactNode;
}>;

export function AdminSideShell({
  title,
  menuItems,
  selectedKey,
  topExtra,
  children,
}: Props) {
  return (
    <XftAdminSideShell
      title={title}
      menuItems={menuItems}
      selectedKey={selectedKey}
      topExtra={topExtra}
    >
      {children}
    </XftAdminSideShell>
  );
}
