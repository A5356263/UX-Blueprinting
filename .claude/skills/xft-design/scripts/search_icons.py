#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search XFT local icon registry and output ICON_DECISION JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "icons.csv"


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize(text: Any) -> str:
    return str(text or "").lower().strip()


def tokenize(text: Any) -> List[str]:
    raw = normalize(text)
    if not raw:
        return []
    parts = re.split(r"[\s,，、。;；:：/\\()（）\[\]{}<>|+_-]+", raw)
    tokens: List[str] = []
    for part in parts:
        if not part:
            continue
        tokens.append(part)
        if re.search(r"[\u4e00-\u9fff]", part) and len(part) >= 2:
            for n in (2, 3):
                if len(part) >= n:
                    tokens.extend(part[i : i + n] for i in range(0, len(part) - n + 1))
    return [t for t in tokens if len(t) >= 2]


class BM25:
    def __init__(self, docs: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs_tokens = [tokenize(doc) for doc in docs]
        self.doc_lens = [len(doc) for doc in self.docs_tokens]
        self.avgdl = sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 0
        self.idf: Dict[str, float] = {}
        df: Counter[str] = Counter()
        for doc in self.docs_tokens:
            for token in set(doc):
                df[token] += 1
        n_docs = len(self.docs_tokens)
        for token, freq in df.items():
            self.idf[token] = math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1)

    def scores(self, query: str) -> List[float]:
        query_tokens = tokenize(query)
        out: List[float] = []
        for doc, doc_len in zip(self.docs_tokens, self.doc_lens):
            tf = Counter(doc)
            score = 0.0
            for token in query_tokens:
                if token not in self.idf:
                    continue
                freq = tf[token]
                denom = freq + self.k1 * (1 - self.b + self.b * doc_len / (self.avgdl or 1))
                score += self.idf[token] * (freq * (self.k1 + 1)) / (denom or 1)
            out.append(score)
        return out


def keyword_bonus(query: str, row: Dict[str, str], fields: List[str], weight: float = 1.0) -> float:
    q_tokens = set(tokenize(query))
    text = normalize(" ".join(row.get(field, "") for field in fields))
    score = 0.0
    for token in q_tokens:
        if token and token in text:
            score += weight
    return score


def row_doc(row: Dict[str, str]) -> str:
    return " ".join(
        [
            row.get("category", ""),
            row.get("icon_name", ""),
            row.get("keywords", ""),
            row.get("usage", ""),
            row.get("best_for", ""),
            row.get("notes", ""),
        ]
    )


def rank_icons(query: str, rows: List[Dict[str, str]], max_results: int = 8) -> List[Tuple[float, Dict[str, str]]]:
    if not rows:
        return []
    docs = [row_doc(row) for row in rows]
    bm25 = BM25(docs)
    bm25_scores = bm25.scores(query)
    ranked: List[Tuple[float, Dict[str, str]]] = []
    for row, bm25_score in zip(rows, bm25_scores):
        score = bm25_score + keyword_bonus(query, row, ["keywords", "best_for", "usage"], 1.5)
        ranked.append((score, row))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item for item in ranked[:max_results] if item[0] > 0]


def build_icon_entry(row: Dict[str, str], score: float) -> Dict[str, Any]:
    svg_path = row.get("svg_path", "")
    return {
        "icon_name": row.get("icon_name", ""),
        "category": row.get("category", ""),
        "usage": row.get("usage", ""),
        "best_for": row.get("best_for", ""),
        "style": row.get("style", ""),
        "svg_path": svg_path,
        "exists": bool(svg_path and (ROOT / svg_path).exists()),
        "match_score": round(score, 4),
    }


def build_decision(query: str, data_file: Path = DATA_FILE, max_results: int = 8) -> Dict[str, Any]:
    rows = read_csv(data_file)
    ranked = rank_icons(query, rows, max_results=max_results)
    selected = [build_icon_entry(row, score) for score, row in ranked]
    missing = [item for item in selected if not item["exists"]]
    return {
        "decision_type": "ICON_DECISION",
        "query": query,
        "source": str(data_file.relative_to(ROOT)).replace("\\", "/"),
        "icons": selected,
        "unsupported": [
            {
                "icon_name": item["icon_name"],
                "reason": "svg_path_missing",
                "svg_path": item["svg_path"],
            }
            for item in missing
        ],
        "validation_targets": [
            "icon_registry_exists",
            "icon_svg_paths_exist",
            "icons_from_local_registry_only",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search XFT icon registry and output ICON_DECISION JSON.")
    parser.add_argument("query", help="用户页面需求")
    parser.add_argument("--data-file", default=str(DATA_FILE), help="icon registry csv path")
    parser.add_argument("--max-results", type=int, default=8, help="max icon results")
    parser.add_argument("--pretty", action="store_true", help="pretty JSON output")
    args = parser.parse_args()
    decision = build_decision(args.query, Path(args.data_file), max_results=args.max_results)
    print(json.dumps(decision, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
