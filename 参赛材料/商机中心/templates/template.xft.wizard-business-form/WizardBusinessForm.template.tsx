import React, { ReactNode } from "react";
import { Alert, Button, Flex, Steps, Typography } from "antd";
import "./WizardBusinessForm.css";

export type WizardBusinessStep = { key: string; title: string; content: ReactNode; description?: string; status?: "wait" | "process" | "finish" | "error" };
export type WizardBusinessFormProps = { title: string; steps: WizardBusinessStep[]; current: number; notice?: string; errorSummary?: ReactNode; onSaveDraft?: () => void; onBack: () => void; onNext: () => void; onSubmit: () => void };

export function WizardBusinessForm({ title, steps, current, notice, errorSummary, onSaveDraft, onBack, onNext, onSubmit }: WizardBusinessFormProps) {
  const finalStep = current === steps.length - 1;
  return <section className="wizard-business-form">
    <Typography.Title className="wizard-business-form__title" level={2}>{title}</Typography.Title>
    <Steps current={current} items={steps.map(({ title, description, status }) => ({ title, description, status }))} />
    {notice ? <Alert type="info" showIcon message={notice} /> : null}
    {errorSummary ? <section className="wizard-business-form__error-summary" aria-label="Stage errors">{errorSummary}</section> : null}
    <section className="wizard-business-form__stage"><Typography.Title className="wizard-business-form__stage-title" level={4}>{steps[current]?.title}</Typography.Title>{steps[current]?.content}</section>
    <footer className="wizard-business-form__footer"><Flex justify="space-between"><Button disabled={current === 0} onClick={onBack}>Back</Button><Flex gap="small">{onSaveDraft ? <Button onClick={onSaveDraft}>Save draft</Button> : null}<Button type="primary" onClick={finalStep ? onSubmit : onNext}>{finalStep ? "Submit" : "Continue"}</Button></Flex></Flex></footer>
  </section>;
}
