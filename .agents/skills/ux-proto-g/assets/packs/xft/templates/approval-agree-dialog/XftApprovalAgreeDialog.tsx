import React, { useRef, useState } from "react";
import { Button, Divider, Dropdown, Image, Input, message, Modal, Upload } from "antd";
import { CheckCircleFilled, CloseCircleFilled, DeleteOutlined, PaperClipOutlined, PictureOutlined } from "@ant-design/icons";
import "./XftApprovalAgreeDialog.css";

export type XftApprovalAgreeSignatureMode = "hidden" | "optional" | "required";
export type XftApprovalAgreeFile = { name: string; dataUrl: string };
export type XftApprovalAgreeValue = {
  opinion: string;
  images: XftApprovalAgreeFile[];
  attachments: XftApprovalAgreeFile[];
  signature?: string;
};
export type XftApprovalAgreeDialogProps = {
  open: boolean;
  onCancel: () => void;
  onAgree: (value: XftApprovalAgreeValue) => void;
  opinionRequired?: boolean;
  signatureMode?: XftApprovalAgreeSignatureMode;
  commonPhrases?: string[];
};

type SignaturePadProps = { onDone: (dataUrl: string) => void; onCancel: () => void };
function SignaturePad({ onDone, onCancel }: SignaturePadProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const [hasStroke, setHasStroke] = useState(false);
  const point = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current!;
    const bounds = canvas.getBoundingClientRect();
    return { x: (event.clientX - bounds.left) * canvas.width / bounds.width, y: (event.clientY - bounds.top) * canvas.height / bounds.height };
  };
  return <Modal className="xft-approval-signature" open title="手写签名" width={740} onCancel={onCancel} footer={<><Button onClick={() => { canvasRef.current?.getContext("2d")?.clearRect(0, 0, 1000, 400); setHasStroke(false); }}>清空</Button><Button type="primary" disabled={!hasStroke} onClick={() => onDone(canvasRef.current!.toDataURL("image/png"))}>确定</Button></>}>
    <canvas ref={canvasRef} width={1000} height={400} aria-label="签名区" onPointerDown={(event) => { const canvas = canvasRef.current!; canvas.setPointerCapture(event.pointerId); const ctx = canvas.getContext("2d")!; const p = point(event); ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineWidth = 2.5; ctx.lineCap = "round"; ctx.strokeStyle = "#1f1f1f"; drawing.current = true; }} onPointerMove={(event) => { if (!drawing.current) return; const ctx = canvasRef.current!.getContext("2d")!; const p = point(event); ctx.lineTo(p.x, p.y); ctx.stroke(); setHasStroke(true); }} onPointerUp={() => { drawing.current = false; }} />
  </Modal>;
}

export function XftApprovalAgreeDialog({ open, onCancel, onAgree, opinionRequired = false, signatureMode = "optional", commonPhrases }: XftApprovalAgreeDialogProps) {
  const [opinion, setOpinion] = useState("");
  const [images, setImages] = useState<XftApprovalAgreeFile[]>([]);
  const [attachments, setAttachments] = useState<XftApprovalAgreeFile[]>([]);
  const [signature, setSignature] = useState<string>();
  const [signatureOpen, setSignatureOpen] = useState(false);
  const [attempted, setAttempted] = useState(false);
  const invalidOpinion = attempted && opinionRequired && !opinion.trim();
  const invalidSignature = attempted && signatureMode === "required" && !signature;
  const addFiles = (files: File[], kind: "images" | "attachments") => files.forEach((file) => {
    const reader = new FileReader();
    reader.onload = () => {
      const item = { name: file.name, dataUrl: String(reader.result) };
      if (kind === "images") setImages((current) => [...current, item]);
      else setAttachments((current) => [...current, item]);
    };
    reader.readAsDataURL(file);
  });
  const submit = () => {
    setAttempted(true);
    if (opinionRequired && !opinion.trim() || signatureMode === "required" && !signature) { message.warning("必填项未填写"); return; }
    onAgree({ opinion: opinion.trim(), images, attachments, signature });
  };
  return <><Modal className="xft-approval-agree" open={open} width={480} title={<span className="xft-approval-agree__title"><CheckCircleFilled />同意</span>} onCancel={onCancel} footer={<><Button onClick={onCancel}>取消</Button><Button type="primary" onClick={submit}>同意</Button></>}>
    <div className="xft-approval-agree__body">
      <div className="xft-approval-agree__opinion">
        <Input.TextArea value={opinion} onChange={(event) => setOpinion(event.target.value)} placeholder="请输入同意意见" className={invalidOpinion ? "xft-approval-agree__invalid" : ""} style={{ height: 98, resize: "none" }} autoSize={false} />
        {invalidOpinion && <div className="xft-approval-agree__error">必填项未填写</div>}
      </div>
      <div className="xft-approval-agree__toolbar">
        <Upload showUploadList={false} beforeUpload={(file) => { addFiles([file], "images"); return false; }} accept="image/*"><Button type="text" icon={<PictureOutlined />}>图片</Button></Upload>
        <Divider type="vertical" className="xft-approval-agree__toolbar-divider" />
        <Upload showUploadList={false} beforeUpload={(file) => { addFiles([file], "attachments"); return false; }}><Button type="text" icon={<PaperClipOutlined />}>附件</Button></Upload>
        <Dropdown menu={{ items: commonPhrases?.map((phrase, index) => ({ key: String(index), label: phrase, onClick: () => setOpinion((current) => current ? `${current}\n${phrase}` : phrase) })) ?? [] }} disabled={!commonPhrases?.length}><Button type="text">常用语⌄</Button></Dropdown>
      </div>
      {!!images.length && <div className="xft-approval-agree__images">{images.map((item, index) => <div key={`${item.name}-${index}`}><Image src={item.dataUrl} alt={item.name} width={64} height={64} /><Button aria-label={`移除 ${item.name}`} size="small" type="text" icon={<DeleteOutlined />} onClick={() => setImages((current) => current.filter((_, i) => i !== index))} /></div>)}</div>}
      {!!attachments.length && <div className="xft-approval-agree__files">{attachments.map((item, index) => <div key={`${item.name}-${index}`}><PaperClipOutlined /><span>{item.name}</span><Button size="small" type="link" href={item.dataUrl} download={item.name}>下载</Button><Button size="small" type="text" icon={<DeleteOutlined />} onClick={() => setAttachments((current) => current.filter((_, i) => i !== index))} /></div>)}</div>}
      {signatureMode !== "hidden" && <div className="xft-approval-agree__signature">{signature ? <div className="xft-approval-agree__signature-preview"><Image src={signature} alt="手写签名" width={90} height={42} /><Button className="xft-approval-agree__signature-remove" aria-label="移除签名" title="移除签名" size="small" type="text" icon={<CloseCircleFilled />} onClick={() => setSignature(undefined)} /></div> : <Button onClick={() => setSignatureOpen(true)}>签名</Button>}{invalidSignature && <div className="xft-approval-agree__error">必填项未填写</div>}</div>}
    </div>
  </Modal>{signatureOpen && <SignaturePad onCancel={() => setSignatureOpen(false)} onDone={(dataUrl) => { setSignature(dataUrl); setSignatureOpen(false); }} />}</>;
}
