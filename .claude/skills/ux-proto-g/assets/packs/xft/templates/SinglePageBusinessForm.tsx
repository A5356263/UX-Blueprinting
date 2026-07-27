import React, { ReactNode } from "react";
import { Button, Flex, Typography } from "antd";
import "./SinglePageBusinessForm.css";

export type BusinessFormSection = { id: string; title: string; content: ReactNode };
export type SinglePageBusinessFormProps = { title: string; sections: BusinessFormSection[]; draftStatus?: ReactNode; errorSummary?: ReactNode; onSaveDraft?: () => void; onSubmit: () => void; submitLabel?: string };

export function SinglePageBusinessForm({ title, sections, draftStatus, errorSummary, onSaveDraft, onSubmit, submitLabel = "Submit" }: SinglePageBusinessFormProps) {
  return <section className="single-business-form">
    <header className="single-business-form__header"><Typography.Title className="single-business-form__title" level={2}>{title}</Typography.Title>{draftStatus ? <div className="single-business-form__draft-status">{draftStatus}</div> : null}</header>
    {errorSummary ? <section className="single-business-form__error-summary" aria-label="Form errors">{errorSummary}</section> : null}
    <div className="single-business-form__body">
      <nav className="single-business-form__anchor" aria-label="Form sections">{sections.map((section) => <a key={section.id} href={`#${section.id}`}>{section.title}</a>)}</nav>
      <div className="single-business-form__sections">{sections.map((section) => <section id={section.id} key={section.id} className="single-business-form__section"><Typography.Title className="single-business-form__section-title" level={4}>{section.title}</Typography.Title>{section.content}</section>)}</div>
    </div>
    <footer className="single-business-form__footer"><Flex gap="small">{onSaveDraft ? <Button onClick={onSaveDraft}>Save draft</Button> : null}<Button type="primary" onClick={onSubmit}>{submitLabel}</Button></Flex></footer>
  </section>;
}
