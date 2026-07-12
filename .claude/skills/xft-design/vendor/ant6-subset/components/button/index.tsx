import { forwardRef, useEffect, useMemo, useState } from "react";
import type { ButtonHTMLAttributes, MouseEventHandler, ReactNode } from "react";

export type Ant6SubsetButtonVariant = "primary" | "default" | "text";

export type Ant6SubsetButtonProps = {
  variant?: Ant6SubsetButtonVariant;
  disabled?: boolean;
  loading?: boolean | { delay?: number };
  block?: boolean;
  autoInsertSpace?: boolean;
  children: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
} & Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children" | "onClick" | "disabled">;

const rxTwoCNChar = /^[\u4E00-\u9FA5]{2}$/;

function isTwoCNChar(text: string) {
  return rxTwoCNChar.test(text);
}

function getLoadingConfig(loading: Ant6SubsetButtonProps["loading"]) {
  if (typeof loading === "object" && loading !== null) {
    const delay = typeof loading.delay === "number" ? loading.delay : 0;
    return {
      loading: delay <= 0,
      delay,
    };
  }

  return {
    loading: Boolean(loading),
    delay: 0,
  };
}

function renderContent(children: ReactNode, autoInsertSpace: boolean) {
  if (typeof children !== "string") {
    return children;
  }

  if (!autoInsertSpace || !isTwoCNChar(children)) {
    return children;
  }

  return children.split("").join(" ");
}

export const Ant6SubsetButton = forwardRef<HTMLButtonElement, Ant6SubsetButtonProps>(
  function Ant6SubsetButton(
    {
      variant = "default",
      disabled = false,
      loading = false,
      block = false,
      autoInsertSpace = true,
      children,
      className,
      type = "button",
      onClick,
      ...rest
    },
    ref,
  ) {
    const loadingConfig = useMemo(() => getLoadingConfig(loading), [loading]);
    const [innerLoading, setInnerLoading] = useState(loadingConfig.loading);

    useEffect(() => {
      let delayTimer: ReturnType<typeof setTimeout> | null = null;

      if (loadingConfig.delay > 0) {
        delayTimer = setTimeout(() => {
          setInnerLoading(true);
          delayTimer = null;
        }, loadingConfig.delay);
      } else {
        setInnerLoading(loadingConfig.loading);
      }

      return () => {
        if (delayTimer) {
          clearTimeout(delayTimer);
        }
      };
    }, [loadingConfig.delay, loadingConfig.loading]);

    const mergedDisabled = disabled || innerLoading;
    const classes = [
      "xft-button",
      `xft-button--${variant}`,
      block ? "xft-button--block" : "",
      innerLoading ? "xft-button--loading" : "",
      className ?? "",
    ]
      .filter(Boolean)
      .join(" ");

    const content = renderContent(children, autoInsertSpace);

    return (
      <button
        {...rest}
        ref={ref}
        type={type}
        className={classes}
        disabled={mergedDisabled}
        onClick={(event) => {
          if (mergedDisabled) {
            event.preventDefault();
            return;
          }

          onClick?.(event);
        }}
      >
        {innerLoading ? <span className="xft-button__loading-dot" aria-hidden="true" /> : null}
        <span className="xft-button__content">{innerLoading ? "加载中" : content}</span>
      </button>
    );
  },
);

