import React, { ReactNode } from "react";
import "./XftSectionHeading.css";

export type XftSectionHeadingProps = {
  title: ReactNode;
  description?: ReactNode;
  titleActions?: ReactNode;
  actions?: ReactNode;
  marker?: boolean;
};

export function XftSectionHeading({ title, description, titleActions, actions, marker = true }: XftSectionHeadingProps) {
  return <header className="xft-section-heading">
    <div className="xft-section-heading__main">
      <div className="xft-section-heading__title-row">
        <div className="xft-section-heading__title-content">
          <div className="xft-section-heading__title-label">
            {marker ? <span className="xft-section-heading__marker" aria-hidden="true" /> : null}
            <h3 className="xft-section-heading__title">{title}</h3>
          </div>
          {titleActions ? <div className="xft-section-heading__title-actions">{titleActions}</div> : null}
        </div>
        {actions ? <div className="xft-section-heading__actions">{actions}</div> : null}
      </div>
      {description ? <div className="xft-section-heading__description">{description}</div> : null}
    </div>
  </header>;
}
