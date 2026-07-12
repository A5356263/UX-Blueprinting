import type { PropsWithChildren, ReactNode } from "react";
import { XftModal } from "../../../vendor/ant6-subset/adapters/xft-modal";

type Props = PropsWithChildren<{
  open: boolean;
  title: ReactNode;
  footer?: ReactNode;
  onClose?: () => void;
}>;

export function ModalTask({ open, title, footer, onClose, children }: Props) {
  return (
    <XftModal open={open} title={title} footer={footer} onClose={onClose}>
      {children}
    </XftModal>
  );
}
