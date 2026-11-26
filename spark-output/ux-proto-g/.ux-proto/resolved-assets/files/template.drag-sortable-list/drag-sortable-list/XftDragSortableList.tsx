import React, { type ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Tooltip } from "antd";
import { HolderOutlined } from "@ant-design/icons";
import "./XftDragSortableList.css";

export type XftDragSortItem = { key: string; content: ReactNode };
export type XftDragSortableListProps = {
  items: XftDragSortItem[];
  onOrderChange: (keys: string[]) => void;
  handleIcon?: ReactNode;
};

type PendingDrag = {
  key: string;
  pointerId: number;
  startY: number;
  offsetY: number;
  initialOrder: string[];
  active: boolean;
  cleanup: () => void;
};

const rowHeight = 46;
const rowGap = 0;

export function XftDragSortableList({ items, onOrderChange, handleIcon }: XftDragSortableListProps) {
  const itemKeys = JSON.stringify(items.map((item) => item.key));
  const [order, setOrder] = useState(() => items.map((item) => item.key));
  const [drag, setDrag] = useState<{ key: string; top: number } | null>(null);
  const orderRef = useRef(order);
  const pendingRef = useRef<PendingDrag | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const rowRefs = useRef(new Map<string, HTMLDivElement>());
  const previousRects = useRef(new Map<string, DOMRect>());

  useEffect(() => {
    if (pendingRef.current?.active) return;
    const next = items.map((item) => item.key);
    orderRef.current = next;
    setOrder(next);
  }, [itemKeys]);

  useEffect(() => () => pendingRef.current?.cleanup(), []);

  useLayoutEffect(() => {
    for (const [key, before] of previousRects.current) {
      const row = rowRefs.current.get(key);
      if (!row) continue;
      row.getAnimations().forEach((animation) => animation.cancel());
      const distance = before.top - row.getBoundingClientRect().top;
      if (Math.abs(distance) > 1) row.animate(
        [{ transform: `translateY(${distance}px)` }, { transform: "translateY(0)" }],
        { duration: 300, easing: "linear" }
      );
    }
    previousRects.current.clear();
  }, [order]);

  const changeOrder = (next: string[]) => {
    previousRects.current = new Map([...rowRefs.current].map(([key, row]) => [key, row.getBoundingClientRect()]));
    orderRef.current = next;
    setOrder(next);
  };

  const onPointerDown = (event: React.PointerEvent<HTMLButtonElement>, key: string) => {
    if (pendingRef.current || event.pointerType === "mouse" && event.button !== 0) return;
    const row = rowRefs.current.get(key);
    if (!row) return;
    event.preventDefault();
    const onUp = (pointerEvent: PointerEvent) => finishDrag(pointerEvent.pointerId, false);
    const onCancel = (pointerEvent: PointerEvent) => finishDrag(pointerEvent.pointerId, true);
    const onBlur = () => finishDrag(event.pointerId, true);
    const cleanup = () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onCancel);
      window.removeEventListener("blur", onBlur);
    };
    pendingRef.current = {
      key, pointerId: event.pointerId, startY: event.clientY,
      offsetY: event.clientY - row.getBoundingClientRect().top,
      initialOrder: [...orderRef.current], active: false, cleanup
    };
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onCancel);
    window.addEventListener("blur", onBlur);
  };

  const onPointerMove = (event: PointerEvent) => {
    const pending = pendingRef.current;
    const list = listRef.current;
    if (!pending || !list || pending.pointerId !== event.pointerId) return;
    if (!pending.active && Math.abs(event.clientY - pending.startY) < 4) return;
    pending.active = true;
    const listBounds = list.getBoundingClientRect();
    const top = Math.max(0, Math.min(
      event.clientY - listBounds.top + list.scrollTop - pending.offsetY,
      (orderRef.current.length - 1) * (rowHeight + rowGap)
    ));
    setDrag({ key: pending.key, top });

    const next = [...orderRef.current];
    const from = next.indexOf(pending.key);
    let to = from;
    while (to > 0 && top < (to - 1) * (rowHeight + rowGap) + rowHeight / 2) to -= 1;
    while (to < next.length - 1 && top + rowHeight > (to + 1) * (rowHeight + rowGap) + rowHeight / 2) to += 1;
    if (to !== from) {
      next.splice(from, 1);
      next.splice(to, 0, pending.key);
      changeOrder(next);
    }
  };

  const finishDrag = (pointerId: number, cancelled: boolean) => {
    const pending = pendingRef.current;
    if (!pending || pending.pointerId !== pointerId) return;
    pending.cleanup();
    pendingRef.current = null;
    setDrag(null);
    if (cancelled) {
      if (pending.active) changeOrder(pending.initialOrder);
      return;
    }
    if (pending.active && orderRef.current.some((key, index) => key !== pending.initialOrder[index])) {
      onOrderChange([...orderRef.current]);
    }
  };

  const onHandleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, key: string) => {
    const step = event.key === "ArrowUp" ? -1 : event.key === "ArrowDown" ? 1 : 0;
    if (!step) return;
    event.preventDefault();
    const from = orderRef.current.indexOf(key);
    const to = from + step;
    if (to < 0 || to >= orderRef.current.length) return;
    const next = [...orderRef.current];
    next.splice(from, 1);
    next.splice(to, 0, key);
    changeOrder(next);
    onOrderChange(next);
  };

  const itemByKey = new Map(items.map((item) => [item.key, item]));
  const visibleKeys = order.filter((key) => itemByKey.has(key));
  const draggedItem = drag && itemByKey.get(drag.key);
  const icon = handleIcon ?? <HolderOutlined />;

  return <div ref={listRef} role="list" className={`xft-drag-sortable-list${drag ? " xft-drag-sortable-list--dragging" : ""}`}>
    {visibleKeys.map((key) => {
      const item = itemByKey.get(key)!;
      return <div key={key} ref={(row) => { if (row) rowRefs.current.set(key, row); else rowRefs.current.delete(key); }} role="listitem" className={`xft-drag-sortable-list__row${drag?.key === key ? " xft-drag-sortable-list__row--placeholder" : ""}`}>
        <Tooltip title="拖拽调整顺序" color="var(--alias-surface-region-inverse)" open={drag ? false : undefined}>
          <button type="button" className="xft-drag-sortable-list__handle" aria-label="拖拽调整顺序" aria-keyshortcuts="ArrowUp ArrowDown" onPointerDown={(event) => onPointerDown(event, key)} onKeyDown={(event) => onHandleKeyDown(event, key)}>{icon}</button>
        </Tooltip>
        <div className="xft-drag-sortable-list__content">{item.content}</div>
      </div>;
    })}
    {draggedItem && <div aria-hidden="true" className="xft-drag-sortable-list__row xft-drag-sortable-list__row--ghost" style={{ transform: `translateY(${drag.top}px)` }}><span className="xft-drag-sortable-list__handle">{icon}</span><div className="xft-drag-sortable-list__content">{draggedItem.content}</div></div>}
  </div>;
}
