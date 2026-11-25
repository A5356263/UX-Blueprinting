import React from "react";
import { Pagination } from "antd";
import "./XftSelectionPaginationBar.css";
export type XftSelectionPagination = { current: number; pageSize?: number; total: number; onChange: (page: number, pageSize: number) => void };
export type XftSelectionPaginationBarProps = { selectedCount?: number; pagination?: XftSelectionPagination };
export function XftSelectionPaginationBar({ selectedCount, pagination }: XftSelectionPaginationBarProps) { if (!pagination && selectedCount === undefined) return null; const normalizedPagination = pagination ? { ...pagination, pageSize: pagination.pageSize ?? 10 } : null; return <footer className={`xft-selection-pagination-bar${selectedCount === undefined ? "" : " xft-selection-pagination-bar--has-selection"}`}>{selectedCount === undefined ? null : <span>已选 {selectedCount} 条</span>}{normalizedPagination ? <Pagination {...normalizedPagination} showSizeChanger showQuickJumper={{ goButton: "跳转" }} showTotal={(total) => <span>共 {total} 条</span>} /> : null}</footer>; }
