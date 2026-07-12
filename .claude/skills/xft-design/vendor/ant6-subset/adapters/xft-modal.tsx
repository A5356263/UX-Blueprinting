import type { PropsWithChildren, ReactNode } from "react";

export type XftModalProps = PropsWithChildren<{
  open: boolean;
  title: ReactNode;
  footer?: ReactNode;
  onClose?: () => void;
}>;

export function XftModal({
  open,
  title,
  footer,
  onClose,
  children,
}: XftModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="xft-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="xft-modal"
        role="dialog"
        aria-modal="true"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="xft-modal__header">
          <div className="xft-modal__title">{title}</div>
          <button type="button" className="xft-modal__close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="xft-modal__body">{children}</div>
        {footer ? <div className="xft-modal__footer">{footer}</div> : null}
      </div>
    </div>
  );
}
