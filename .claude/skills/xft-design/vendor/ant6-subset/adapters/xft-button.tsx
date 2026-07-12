import type { MouseEventHandler, ReactNode } from "react";
import {
  Ant6SubsetButton,
  type Ant6SubsetButtonVariant,
} from "../components/button";

export type XftButtonVariant = Ant6SubsetButtonVariant;

export type XftButtonProps = {
  variant?: XftButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  block?: boolean;
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
};

export function XftButton({
  variant = "default",
  disabled = false,
  loading = false,
  block = false,
  children,
  onClick,
}: XftButtonProps) {
  return (
    <Ant6SubsetButton
      type="button"
      variant={variant}
      disabled={disabled}
      loading={loading}
      block={block}
      onClick={onClick}
    >
      {children}
    </Ant6SubsetButton>
  );
}

